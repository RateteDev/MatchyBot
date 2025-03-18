import os
import sys
import logging
from dotenv import load_dotenv
from matchybot.bot import MyDiscordBot, setup_bot

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # 環境変数の読み込み
    load_dotenv()

    # 環境変数にBOT_TOKENが設定されているか確認
    if not os.getenv("BOT_TOKEN"):
        logger.error("BOT_TOKEN is not set in .env file. Please set it.")
        sys.exit(1)

    # ボットのセットアップと起動
    bot: MyDiscordBot = setup_bot()
    bot.run(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    main()
