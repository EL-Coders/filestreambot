from importlib import import_module
from pathlib import Path
from bot import TelegramBot, logger, start_streaming_bots
from bot.config import Telegram
from bot.server import server
from bot.utils import ping, restart


def load_plugins():
    count = 0
    for path in Path("bot/plugins").rglob("*.py"):
        import_module(f"bot.plugins.{path.stem}")
        count += 1
    logger.info("Loaded %s %s.", count, "plugins" if count > 1 else "plugin")


if __name__ == "__main__":
    logger.info("initializing...")
    TelegramBot.loop.create_task(server.serve())
    TelegramBot.loop.create_task(ping.ping_server())
    TelegramBot.loop.create_task(restart.restart_bot())
    TelegramBot.start(bot_token=Telegram.BOT_TOKEN)
    logger.info("Telegram client is now started.")

    TelegramBot.loop.run_until_complete(start_streaming_bots())

    logger.info("Loading bot plugins...")
    load_plugins()
    logger.info("Bot is now ready!")
    TelegramBot.run_until_disconnected()
