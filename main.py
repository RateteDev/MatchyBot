# /src/matchybot/main.py

from matchybot.bot import setup_bot
from logging import getLogger
from dotenv import load_dotenv

logger = getLogger(__name__)
load_dotenv()

# BOTのセットアップ
bot, token = setup_bot()

# BOTの起動
bot.run(token)


