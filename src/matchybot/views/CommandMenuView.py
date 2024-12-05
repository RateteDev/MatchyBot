# /src/matchybot/views/CommandMenuView.py

import discord
from discord.ui import View, Button
from matchybot.views.RegisterView import RegisterView
from matchybot.views.RecruitView import RecruitView

class CommandMenuView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        
        # ランク登録ボタン
        register_button = Button(
            label="ランク登録", 
            style=discord.ButtonStyle.primary,
            custom_id="register_rank"
        )
        register_button.callback = self.register_callback
        self.add_item(register_button)

        # 募集開始ボタン
        start_button = Button(
            label="募集開始", 
            style=discord.ButtonStyle.primary,
            custom_id="start_recruit"
        )
        start_button.callback = self.start_callback
        self.add_item(start_button)

    
    async def register_callback(self, interaction: discord.Interaction):
        # RegisterViewを使用してインタラクションを開始
        view = RegisterView(interaction=interaction, bot=self.bot)
        await interaction.response.send_message(
            "ランクを登録してください。",
            view=view,
            ephemeral=True
        ) 
    
    async def start_callback(self, interaction: discord.Interaction):
        # 募集開始ボタンの処理を実装
        view = RecruitView(bot=self.bot)
        embed = await view.create_embed()
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=False
        )
