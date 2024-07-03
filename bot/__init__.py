from logging import getLogger
from logging.config import dictConfig
from telethon import TelegramClient
from .config import LOGGER_CONFIG_JSON, Telegram

dictConfig(LOGGER_CONFIG_JSON)

version = 1.5
logger = getLogger("bot")

TelegramBot = TelegramClient(
    session="bot", api_id=Telegram.API_ID, api_hash=Telegram.API_HASH
)
