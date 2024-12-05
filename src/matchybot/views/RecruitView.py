# /src/matchybot/views/RecruitView.py
import discord
from discord.ui import View, Button
from matchybot.models.Recruitment import Recruitment, Player
from logging import getLogger

logger = getLogger(__name__)

class RecruitView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.recruitment = Recruitment() # 振り分け処理を行うためのRecruitmentクラスをインスタンス化

    @discord.ui.button(label="参加", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: Button):
        try:
            user_id = str(interaction.user.id)
            user_name = interaction.user.display_name

            # プレイヤーデータを取得
            players = self.bot.player_data_manager.get_players()
            player = next((p for p in players if p["id"] == user_id), None)

            # プレイヤーが存在しない、またはランクが登録されていない場合はエラーメッセージを送信
            if not player or "highest_rank" not in player:
                await interaction.response.send_message(
                    "ランク登録が必要です。`/register`コマンドでランクを登録してください。",
                    ephemeral=True
                )
                return

            # エントリーを追加
            if self.recruitment.add_entry(
                user_id=user_id,
                name=user_name,
            ):
                # メッセージを更新
                await interaction.response.edit_message(
                    embed=await self.create_embed(),
                    view=self
                )
            
            # エントリーできない場合はエラーメッセージを送信
            else:
                await interaction.response.send_message(
                    "エントリーでません。（既にエントリー済み、もしくは募集が終了しています）",
                    ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(
                f"エラーが発生しました😭",
                ephemeral=True
            )
            logger.error(e)

    @discord.ui.button(label="参加をキャンセル", style=discord.ButtonStyle.secondary)
    async def leave(self, interaction: discord.Interaction, button: Button):
        try:
            user_id = str(interaction.user.id)
            
            if self.recruitment.remove_entry(user_id):
                # まずメッセージを更新
                await interaction.response.edit_message(
                    embed=await self.create_embed(),
                    view=self
                )
            else:
                await interaction.response.send_message(
                    "エントリーをキャンセルできません。",
                    ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(
                f"参加キャンセル処理に失敗しました😭",
                ephemeral=True
            )
            logger.error(e)

    @discord.ui.button(label="チーム振り分け", style=discord.ButtonStyle.success)
    async def make_teams(self, interaction: discord.Interaction, button: Button):
        try:
            if len(self.recruitment.entries) < 10:
                await interaction.response.send_message(
                    "10人未満での振り分けはできません。最低10人の参加者が必要です。",
                    ephemeral=True
                )
                return

            # プレイヤーのスコアを計算してPlayerオブジェクトのリストを作成
            players_with_scores = []
            for entry in self.recruitment.entries:
                try:
                    score = self._calculate_player_score(entry)
                    player = Player(
                        id=entry["user_id"],
                        name=entry["name"],
                        score=score
                    )
                    players_with_scores.append(player)
                except Exception as e:
                    print(f"Error processing player {entry['name']}: {str(e)}")
                    continue

            # チーム分け実行
            teams = self.recruitment.make_teams(players_with_scores)
            
            if teams:
                embed = self._create_teams_embed(teams)
                
                # チーム分け結果用のチャンネルを取得
                teams_channel = self.bot.get_channel(self.bot.matching_result_channel_id)
                
                if teams_channel:
                    # ボタンリンクを作成
                    view = View()
                    guild_id = 1135527358317740083  # ギルドIDを取得
                    channel_ids = [
                        1197516965951045763,
                        1197516967645556736,
                        1208383961131388968,
                        1208383487728680960
                    ]
                    for i, (team, channel_id) in enumerate(zip(teams, channel_ids), start=1):
                        link = f"https://discord.com/channels/{guild_id}/{channel_id}"
                        button = Button(
                            label=f"チーム {i} VC",
                            url=link,
                            style=discord.ButtonStyle.link
                        )
                        view.add_item(button)
                    
                    # チーム分け結果用チャンネルに結果を送信
                    await teams_channel.send(embed=embed, view=view)
                    # 操作したユーザーにも通知
                    await interaction.response.send_message(
                        f"チーム分け結果を <#{self.bot.matching_result_channel_id}> に送信しました。",
                        ephemeral=True
                    )
                else:
                    # チャンネルが見つからない場合は同じチャンネンに送信
                    await interaction.response.send_message(embed=embed)
                    print(f"Warning: Teams channel (ID: {self.bot.matching_result_channel_id}) not found")
            else:
                await interaction.response.send_message(
                    "⚠️ チーム分けに失敗しました。",
                    ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )

    @discord.ui.button(label="募集を削除", style=discord.ButtonStyle.danger)
    async def delete_recruitment(self, interaction: discord.Interaction, button: Button):
        try:
            # 全てのボタンを無効化
            for item in self.children:
                item.disabled = True

            # 現在のEmbedを取得して色だけを変更
            current_embed = interaction.message.embeds[0]
            current_embed.color = discord.Color.red()
            current_embed.title = "募集終了"

            await interaction.response.edit_message(embed=current_embed, view=self)

        except Exception as e:
            await interaction.response.send_message(
                f"エラーが発生しました: {str(e)}",
                ephemeral=True
            )

    async def create_embed(self) -> discord.Embed:
        """募集用のEmbedを作成"""
        embed = discord.Embed(
            title="カスタムマッチ募集",
            color=discord.Color.blue()
        )
        
        # 参加者数の情報を追加
        embed.add_field(
            name="募集状況",
            value=f"{len(self.recruitment.entries)}人",
            inline=False
        )

        # 参加者リストを10人ずつに分割して表示（縦並び）
        entries = self.recruitment.entries
        chunks = [entries[i:i + 10] for i in range(0, len(entries), 10)]
        
        for i, chunk in enumerate(chunks, 1):
            entries_text = ""
            start_num = (i-1) * 10 + 1
            
            for j, entry in enumerate(chunk, start_num):
                entries_text += f"・{entry['name']}\n"

            if entries_text:
                embed.add_field(
                    name=f"参加者 {start_num}~{start_num + len(chunk) - 1}人目",
                    value=entries_text,
                    inline=False
                )

        return embed

    def _calculate_player_score(self, entry: dict) -> float:
        """プレイヤーのスコアを計算"""
        try:
            if entry["user_id"].isdigit() and int(entry["user_id"]) < 1000:
                # テストプレイヤーの処理
                scores = []
                for role_rank in entry["ranks"].values():
                    score = self._calculate_rank_score(role_rank)
                    scores.append(score)
                return sum(scores) / len(scores) if scores else 0
            else:
                # 通常プレイヤーの処理
                player = next(
                    (p for p in self.bot.player_data_manager.get_players() if p["id"] == entry["user_id"]),
                    None
                )
                if player and "highest_rank" in player:
                    return self._calculate_rank_score(player["highest_rank"])
                return 0
        except Exception as e:
            print(f"Error calculating score: {str(e)}")
            return 0

    def _calculate_rank_score(self, rank_data: dict) -> float:
        """ランクデータからスコアを計算"""
        if not rank_data:
            return 0
            
        rank = rank_data["rank"]
        division = rank_data.get("division")
        
        if rank == "TOP500":
            return 4500
        
        try:
            return rank_data["ranks"][rank][division]
        except KeyError:
            return 0

    def _create_teams_embed(self, teams: list[list[Player]]) -> discord.Embed:
        """チーム分け結果のEmbedを作成"""
        embed = discord.Embed(
            title="チーム分け結果",
            color=discord.Color.blue()
        )
