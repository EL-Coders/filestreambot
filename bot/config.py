from os import environ as env
from dotenv import load_dotenv

load_dotenv()


class Telegram:
    API_ID = int(env.get("TELEGRAM_API_ID", 1234))
    API_HASH = env.get("TELEGRAM_API_HASH", "xyz")
    OWNER_ID = int(env.get("OWNER_ID", 20516707))
    ALLOWED_USER_IDS = env.get("ALLOWED_USER_IDS", "").split()
    BOT_USERNAME = env.get("TELEGRAM_BOT_USERNAME", "InstantLinkELBot")
    BOT_TOKEN = env.get("TELEGRAM_BOT_TOKEN", "")
    CHANNEL_ID = int(env.get("TELEGRAM_CHANNEL_ID", -1001979167499))
    SECRET_CODE_LENGTH = int(env.get("SECRET_CODE_LENGTH", 12))

    @staticmethod
    def get_bot_tokens():
        tokens = []
        if Telegram.BOT_TOKEN:
            tokens.append(Telegram.BOT_TOKEN)
        else:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set")
        count = 1
        while True:
            token = env.get(f"TELEGRAM_BOT_TOKEN_{count}")
            if token:
                tokens.append(token)
                count += 1
            else:
                break
        return tokens


class Server:
    BASE_URL = env.get("BASE_URL", "http://127.0.0.1:8080")
    BIND_ADDRESS = env.get("BIND_ADDRESS", "0.0.0.0")
    PORT = int(env.get("PORT", 8080))
    WORKERS_URL = env.get("WORKERS_URL", "")
    WORKERS_URL_2 = env.get("WORKERS_URL_2", "")
    WORKERS_URL_3 = env.get("WORKERS_URL_3", "")


class DB:
    DB_URL = env.get("DB_URL", "postgresql://uname:pass@locahost:5432/dbname")


class Util:
    PING_INTERVAL = int(env.get("PING_INTERVAL", 1200))  # 20 minutes
    RSTRT_INTERVAL = int(env.get("RSTRT_INTERVAL", 3600))  # 60 minutes
    SUB_CHANNEL = int(env.get("SUB_CHANNEL", 0))
    SUB_CHANNEL_LINK = env.get("SUB_CHANNEL_LINK", "t.me/elupdates")


# LOGGING CONFIGURATION
LOGGER_CONFIG_JSON = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s][%(name)s][%(levelname)s] -> %(message)s",
            "datefmt": "%d/%m/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "filename": "event-log.txt",
            "formatter": "default",
        },
        "stream_handler": {"class": "logging.StreamHandler", "formatter": "default"},
    },
    "loggers": {
        "uvicorn": {"level": "INFO", "handlers": ["file_handler", "stream_handler"]},
        "uvicorn.error": {
            "level": "WARNING",
            "handlers": ["file_handler", "stream_handler"],
        },
        "bot": {"level": "INFO", "handlers": ["file_handler", "stream_handler"]},
        "ping": {"level": "INFO", "handlers": ["file_handler", "stream_handler"]},
        "restarter": {"level": "INFO", "handlers": ["file_handler", "stream_handler"]},
    },
}
