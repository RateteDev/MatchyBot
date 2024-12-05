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

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        await self.send_command_menu()

    async def send_command_menu(self):
        # 登録チャンネルにメッセージを送信
        bot_channel : discord.TextChannel | None = self.get_channel(int(os.getenv("COMMAND_MENU_CHANNEL")))

        # チャンネルが見つからない場合
        if not bot_channel:
            logger.error(f"Bot channel not found: ENV_COMMAND_MENU_CHANNEL={os.getenv('COMMAND_MENU_CHANNEL')}")
            self.close()
            return

        # 既存のメッセージを確認・削除
        async for message in bot_channel.history(limit=100):
            if message.author == self.user:
                await message.delete()
                logger.debug(f"Deleted bot message: {message.id}")
        
        # embedの作成
        embed = discord.Embed(
            title="コマンドメニュー",
            description="コマンドメニューです。",
            color=discord.Color.blue(),
        )

        # 新しいメッセージを送信
        view = CommandMenuView(bot=self)
        await bot_channel.send(
            embed=embed,
            view=view
        )

def setup_bot():
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
    
    return bot, os.getenv("TOKEN")
