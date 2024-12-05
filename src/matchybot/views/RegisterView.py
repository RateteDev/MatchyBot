# /src/matchybot/views/RegisterView.py

import discord
from discord.ui import Button, View, Select
from discord import SelectOption
from matchybot.models.RankDataManager import RankDataManager
from logging import getLogger

logger = getLogger(__name__)

rank_data = RankDataManager("data/rank.json").load_data()

class RegisterView(View):
    def __init__(self, interaction, bot):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.bot = bot
        self.rank = None
        self.division = None
        
        # ランク選択メニュー
        self.rank_select = self.create_rank_select("現在のシーズンの最高ランクを選択してください", 0)
        self.division_select = self.create_division_select("ディビジョンを選択してください", 1)
        
        self.add_item(self.rank_select)
        self.add_item(self.division_select)
        
        # 登録ボタン
        self.submit_button = Button(label="登録", style=discord.ButtonStyle.primary, custom_id="submit", row=2)
        self.submit_button.callback = self.submit
        self.add_item(self.submit_button)

    def update_select_placeholders(self):
        """選択状態を各Selectのプレースホルダーに反映"""
        if self.rank:
            self.rank_select.placeholder = f"選択済み: {self.rank}"
        
        if self.division:
            self.division_select.placeholder = f"選択済み: {self.division}"
        elif self.rank == "TOP500":
            self.division_select.placeholder = "ディビジョンを選択してください"

    def get_rank_options(self):
        # TOP500を含む全ランクのリストを作成
        ranks = list(rank_data["ranks"].keys())
        return [SelectOption(label=rank, value=rank) for rank in ranks]

    def create_rank_select(self, placeholder: str, row: int) -> Select:
        select = Select(
            placeholder=placeholder,
            options=self.get_rank_options(),
            custom_id="rank_select",
            row=row
        )
        select.callback = self.rank_callback
        return select

    def create_division_select(self, placeholder: str, row: int) -> Select:
        select = Select(
            placeholder=placeholder,
            options=[SelectOption(label=str(i), value=str(i)) for i in range(1, 6)],
            disabled=True,
            custom_id="division_select",
            row=row
        )
        select.callback = self.division_callback
        return select

    async def rank_callback(self, interaction: discord.Interaction):
        self.rank = interaction.data["values"][0]
        
        if self.rank != "TOP500":
            self.division_select.disabled = False
        else:
            self.division_select.disabled = True
            self.division = None
        
        self.update_select_placeholders()
        await interaction.response.edit_message(view=self)

    async def division_callback(self, interaction: discord.Interaction):
        self.division = interaction.data["values"][0]
        self.update_select_placeholders()
        await interaction.response.edit_message(view=self)

    async def submit(self, interaction: discord.Interaction):
        try:
            # 最高ランクが選択されていない場合
            if self.rank is None:
                await interaction.response.send_message(
                    "最高ランクを選択してください。",
                    ephemeral=True
                )
                return

            # ディビジョンが選択されていない場合
            if self.rank != "TOP500" and not self.division:
                await interaction.response.send_message(
                    "ディビジョンを選択してください。",
                    ephemeral=True
                )
                return

            user_id = str(interaction.user.id)
            user_name = interaction.user.name
            players = self.bot.player_data_manager.get_players()

            # ランク情報を設定
            highest_rank = {
                "rank": self.rank,
                "division": self.division if self.rank != "TOP500" else None
            }

            player = next((p for p in players if p["id"] == user_id), None)
            if player is None:
                player = {
                    "id": user_id,
                    "name": user_name,
                    "highest_rank": highest_rank,
                    "recent_matches": []
                }
                players.append(player)
            else:
                player["highest_rank"] = highest_rank

            self.bot.player_data_manager.save_data({"players": players})

            # 登録完了メッセージを作成
            rank_text = highest_rank["rank"]
            if highest_rank["division"]:
                rank_text += f" {highest_rank['division']}"
            response = f"{user_name}さんの最高ランクを{rank_text}で登録しました。"

            # 全ての入力項目を無効化
            self.rank_select.disabled = True
            self.division_select.disabled = True
            self.submit_button.disabled = True
            
            # メッセージを送信し、無効化されたビューを表示
            await interaction.response.edit_message(content=response, view=self)

        except Exception as e:
            if not interaction.response.is_done():
                logger.error(e)
                await interaction.response.send_message(
                    f"エラーが発生しました", ephemeral=True
                )
            else:
                logger.error(e)
                await interaction.followup.send(
                    f"エラーが発生しました", ephemeral=True
                )
