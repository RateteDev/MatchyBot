# /src/matchybot/tests/test_team_balance.py

import random
from ..models.Recruitment import Recruitment

def generate_random_rank():
    ranks = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "TOP500"]
    divisions = ["1", "2", "3", "4", "5"]
    
    rank = random.choice(ranks)
    if rank == "TOP500":
        return {"rank": rank}
    else:
        return {"rank": rank, "division": random.choice(divisions)}

def generate_random_player(player_id: int):
    roles = ["TANK", "DPS", "SUPPORT"]
    # ランダムに1-3個のロールを選択
    selected_roles = random.sample(roles, random.randint(1, 3))
    
    # 各選択されたロールにランクを設定
    ranks = {}
    for role in selected_roles:
        ranks[role] = generate_random_rank()
    
    return {
        "user_id": str(player_id),
        "name": f"TestPlayer{player_id}",
        "roles": selected_roles,
        "ranks": ranks
    }

def test_team_balance():
    # 募集を作成
    recruitment = Recruitment(
        message_id="test_message",
        creator_id="test_creator"
    )
    
    # 10人のランダムなプレイヤーを生成してエントリー
    for i in range(10):
        player = generate_random_player(i)
        recruitment.add_entry(
            user_id=player["user_id"],
            name=player["name"],
            roles=player["roles"],
            ranks=player["ranks"]
        )
    
    # エントリー情報を表示
    print("\n=== エントリー者一覧 ===")
    for entry in recruitment.entries:
        print(f"\nプレイヤー: {entry['name']}")
        for role in entry['roles']:
            rank_info = entry['ranks'][role]
            rank_text = f"{rank_info['rank']}"
            if rank_info.get('division'):
                rank_text += f" {rank_info['division']}"
            print(f"- {role}: {rank_text}")
    
    # チーム分け実行
    team1, team2 = recruitment.create_balanced_teams()
    
    # チーム分け結果を表示
    print("\n=== チーム1 ===")
    team1_avg_score = 0
    for player in team1:
        print(f"\nプレイヤー: {player['name']}")
        player_scores = []
        for role in player['roles']:
            rank_info = player['ranks'][role]
            rank_text = f"{rank_info['rank']}"
            if rank_info.get('division'):
                rank_text += f" {rank_info['division']}"
            print(f"- {role}: {rank_text}")
            score = recruitment.calculate_player_score({role: rank_info})
            player_scores.append(score)
        avg_score = sum(player_scores) / len(player_scores)
        team1_avg_score += avg_score
        print(f"平均スコア: {avg_score:.2f}")
    
    print("\n=== チーム2 ===")
    team2_avg_score = 0
    for player in team2:
        print(f"\nプレイヤー: {player['name']}")
        player_scores = []
        for role in player['roles']:
            rank_info = player['ranks'][role]
            rank_text = f"{rank_info['rank']}"
            if rank_info.get('division'):
                rank_text += f" {rank_info['division']}"
            print(f"- {role}: {rank_text}")
            score = recruitment.calculate_player_score({role: rank_info})
            player_scores.append(score)
        avg_score = sum(player_scores) / len(player_scores)
        team2_avg_score += avg_score
        print(f"平均スコア: {avg_score:.2f}")
    
    team1_avg_score /= len(team1)
    team2_avg_score /= len(team2)
    
    print(f"\n=== チーム平均スコア ===")
    print(f"チーム1: {team1_avg_score:.2f}")
    print(f"チーム2: {team2_avg_score:.2f}")
    print(f"スコア差: {abs(team1_avg_score - team2_avg_score):.2f}")

if __name__ == "__main__":
    test_team_balance()
