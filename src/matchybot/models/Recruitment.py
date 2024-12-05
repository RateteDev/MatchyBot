# /src/matchybot/models/Recruitment.py

from typing import List, Dict, Any
import random
from dataclasses import dataclass
import discord
from .RankDataManager import RankDataManager

@dataclass
class Player:
    id: str
    name: str
    score: float

rank_data = RankDataManager("data/rank.json").load_data()

class Recruitment:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    def add_entry(self, user_id: str, name: str) -> bool:
        # 既にエントリーしている場合は追加しない
        if self.is_user_entered(user_id):
            return False
        
        # エントリーを追加
        self.entries.append({
            "user_id": user_id,
            "name": name
        })

        # 追加成功した場合、Trueを返す
        return True

    def remove_entry(self, user_id: str) -> bool:
        for i, entry in enumerate(self.entries):
            if entry["user_id"] == user_id:
                self.entries.pop(i)
                return True
        return False

    def is_user_entered(self, user_id: str) -> bool:
        for entry in self.entries:
            if entry["user_id"] == user_id:
                return True
        return False

    def calculate_player_score(self, highest_rank: dict) -> float:
        """プレイヤーのスコアを計算"""
        if not highest_rank:
            return 0
            
        rank = highest_rank["rank"]
        division = highest_rank.get("division")
        
        if rank == "TOP500":
            return 4500
        
        try:
            return rank_data["ranks"][rank][division]
        except KeyError:
            return 0

    def balanced_score_teams(self, players: List[Player]) -> list:
        """スコアバランスを重視したチーム分け"""
        if len(players) < 2:
            return []
            
        # プレイヤー数は必ず5の倍数（make_teamsで調整済み）
        num_teams = len(players) // 5
        best_teams = None
        min_score_variance = float('inf')
        
        # 多くの試行でベトな組み合わせを探す
        for _ in range(20):
            # プレイヤーを3つのスコア帯に分類
            players_copy = players.copy()
            players_copy.sort(key=lambda x: x.score, reverse=True)
            
            high_score = players_copy[:len(players_copy)//3]
            mid_score = players_copy[len(players_copy)//3:2*len(players_copy)//3]
            low_score = players_copy[2*len(players_copy)//3:]
            
            # 各スコア帯でシャッフル
            random.shuffle(high_score)
            random.shuffle(mid_score)
            random.shuffle(low_score)
            
            # チーム作成（各チーム5人確定）
            teams = [[] for _ in range(num_teams)]
            
            # 各チームに異なるスコア帯のプレイヤーを分配
            for i in range(num_teams):
                # 上位プレイヤーを1-2人
                high_count = min(len(high_score), random.randint(1, 2))
                for _ in range(high_count):
                    if high_score:
                        teams[i].append(high_score.pop())
                
                # 中位プレイヤーを2人
                mid_count = min(len(mid_score), 2)
                for _ in range(mid_count):
                    if mid_score:
                        teams[i].append(mid_score.pop())
                
                # 下位プレイヤーを残りの枠に（5人になるまで）
                while len(teams[i]) < 5 and low_score:
                    teams[i].append(low_score.pop())
            
            # 余ったプレイヤーがいれば、まだ5人になっていないチームに追加
            remaining = high_score + mid_score + low_score
            for player in remaining:
                for team in teams:
                    if len(team) < 5:
                        team.append(player)
                        break
            
            # チーム間の分散を計算
            team_avgs = [sum(p.score for p in team) / len(team) for team in teams]
            avg_of_avgs = sum(team_avgs) / len(team_avgs)
            variance = sum((x - avg_of_avgs)**2 for x in team_avgs) / len(team_avgs)
            
            # より良いバランスが見つかった場合は更新
            if variance < min_score_variance:
                min_score_variance = variance
                best_teams = [team[:] for team in teams]
                print(f"Found better balance. Variance: {variance:.2f}")
        
        return best_teams if best_teams else teams

    def make_teams(self, players_with_scores: List[Player]) -> list:
        """エントリーしたプレイヤーを5人ずつのチームに分ける"""
        try:
            if len(players_with_scores) < 2:
                print("Not enough players for team division")
                return []

            # プレイヤー数を5の倍数に調整
            total_players = len(players_with_scores)
            target_players = (total_players // 5) * 5
            overflow_count = total_players - target_players
            
            if overflow_count > 0:
                print(f"Removing {overflow_count} overflow players randomly")
                removed_players = random.sample(players_with_scores, overflow_count)
                players_with_scores = [p for p in players_with_scores if p not in removed_players]

            # スコアの高い順にソート
            players_with_scores.sort(key=lambda x: x.score, reverse=True)
            
            print("スコアバランス方式でチーム分け実行")
            return self.balanced_score_teams(players_with_scores)

        except Exception as e:
            print(f"Error in make_teams: {str(e)}")
            return []

    def create_teams_embed(self, teams) -> discord.Embed:
        embed = discord.Embed(
            title="チーム分け結果",
            color=discord.Color.blue()
        )

        # チームに含まれているプレイヤーのIDリスト
        assigned_player_ids = {p["user_id"] for team in teams for p in team}

        # チームを2列で表示するために2つずつ処理
        for i in range(0, len(teams), 2):
            # 左側のチーム（奇数番目）
            team = teams[i]
            team_score = sum(p.score for p in team) / len(team)
            team_text = "\n".join([f"• {p['name']}" for p in sorted(team, key=lambda x: x["score"], reverse=True)])
            embed.add_field(
                name=f"チーム{i+1} (Avg Score: {team_score:.0f})",
                value=team_text,
                inline=True
            )

            # 右側のチーム（偶数番目）が存在する場合
            if i + 1 < len(teams):
                team = teams[i+1]
                team_score = sum(p.score for p in team) / len(team)
                team_text = "\n".join([f"• {p['name']}" for p in sorted(team, key=lambda x: x["score"], reverse=True)])
                embed.add_field(
                    name=f"チーム{i+2} (Avg Score: {team_score:.0f})",
                    value=team_text,
                    inline=True
                )
                
                # 2列目の後に空のフィールドを追加して整列を調整
                embed.add_field(name="\u200b", value="\u200b", inline=True)

        # 余りプレイヤーを表示（最後の行に配置）
        overflow_players = [entry for entry in self.entries if entry["user_id"] not in assigned_player_ids]
        if overflow_players:
            # 前のセクションが3の倍数でない場合、整列のために���フィールドを追加
            if len(embed.fields) % 3 != 0:
                remaining = 3 - (len(embed.fields) % 3)
                for _ in range(remaining):
                    embed.add_field(name="\u200b", value="\u200b", inline=True)
                    
            overflow_text = "\n".join([f"• {p['name']}" for p in overflow_players])
            embed.add_field(
                name="余りプレイヤー",
                value=overflow_text,
                inline=False  # 余りプレイヤーは横幅いっぱいで表示
            )

        return embed
