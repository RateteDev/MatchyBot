# /src/matchybot/bot.py

import os
import sys
import discord
from logging import getLogger
from discord import app_commands
from matchybot.models.PlayerDataManager import PlayerDataManager
from matchybot.views.CommandMenuView import CommandMenuView

logger = getLogger(__name__)

class MyDiscordBot(discord.Client):
    def __init__(self, intents, player_data_manager):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.player_data_manager : PlayerDataManager = player_data_manager

    # ボットの初期化時に1度だけ呼ばれる
    async def setup_hook(self) -> None:
        """初期設定とコマンドの同期を行う"""
        # コマンドを登録
        self.setup_commands()
        # グローバルにコマンドを同期
        try:
            await self.tree.sync()
            logger.info("Synced global commands")
        except discord.errors.HTTPException as e:
            logger.error(f"Failed to sync commands: {e}")

    # ボットが起動したときの処理(再接続でも呼ばれる)
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    # コマンドメニューを表示する機能
    async def send_command_menu(self, interaction: discord.Interaction):
        # embedの作成
        embed = discord.Embed(
            title="コマンドメニュー",
            description="コマンドメニューです。",
            color=discord.Color.blue(),
        )

        # 新しいメッセージを送信
        view = CommandMenuView(bot=self)
        await interaction.response.send_message(
            embed=embed,
            view=view
        )

    # コマンドメニューを表示するコマンドを追加
    def setup_commands(self):
        # コマンドを登録
        menu_command = app_commands.Command(
            name="menu",
            description="コマンドメニューを表示します",
            callback=self.send_command_menu
        )
        self.tree.add_command(menu_command)

def setup_bot() -> MyDiscordBot:
    # インテントの設定
    intents = discord.Intents.all()

    # データマネージャーの設定
    player_data_manager = PlayerDataManager(file_path="data/players.json")
    player_data_manager.load_data()

    # ボットのインスタンス化
    bot = MyDiscordBot(
        intents=intents,
        player_data_manager=player_data_manager,
    )

    return bot
