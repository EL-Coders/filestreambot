from logging import getLogger
from logging.config import dictConfig
from telethon import TelegramClient
from .config import LOGGER_CONFIG_JSON, Telegram
import asyncio

dictConfig(LOGGER_CONFIG_JSON)

version = 1.6
logger = getLogger("bot")

TelegramBot = TelegramClient(
    session="bot", api_id=Telegram.API_ID, api_hash=Telegram.API_HASH
)

_streaming_bots = []
_streaming_tokens = Telegram.get_bot_tokens()
_bot_queue = None
_child_queues = []
_current_child_queue = 0


def initialize_streaming_bots():
    global _streaming_bots, _bot_queue, _child_queues
    if _streaming_bots:
        return

    for i, token in enumerate(_streaming_tokens):
        if i == 0:
            continue
        bot = TelegramClient(
            session=f"stream_bot_{i}",
            api_id=Telegram.API_ID,
            api_hash=Telegram.API_HASH,
        )
        bot._token = token
        _streaming_bots.append(bot)

    _bot_queue = asyncio.Queue()
    _child_queues = [asyncio.Queue() for _ in range(5)]

    logger.info(
        "Initialized %s additional streaming bots with 5 child queues",
        len(_streaming_bots),
    )


async def populate_bot_queue():
    global _bot_queue, _child_queues
    if _bot_queue is None:
        _bot_queue = asyncio.Queue()
        _child_queues = [asyncio.Queue() for _ in range(5)]

    await _bot_queue.put(TelegramBot)
    for bot in _streaming_bots:
        await _bot_queue.put(bot)

    for child_queue in _child_queues:
        await child_queue.put(TelegramBot)
        for bot in _streaming_bots:
            await child_queue.put(bot)

    total_bots = 1 + len(_streaming_bots)
    logger.info("Bot queue populated with %s bots (main + 5 child queues)", total_bots)


async def get_streaming_bot():
    global _bot_queue, _child_queues, _current_child_queue

    try:
        if _bot_queue is None:
            await populate_bot_queue()

        if not _bot_queue.empty():
            bot = await _bot_queue.get()
            logger.debug("Bot acquired from main queue")
            return bot

        for i in range(5):
            queue_index = (_current_child_queue + i) % 5
            child_queue = _child_queues[queue_index]

            if not child_queue.empty():
                bot = await child_queue.get()
                _current_child_queue = (queue_index + 1) % 5
                logger.info("Bot acquired from child queue %s", queue_index + 1)
                return bot

        logger.warning("All queues empty, using main bot as fallback")
        return TelegramBot

    except Exception as e:
        logger.error("Error getting bot from queues: %s", e)
        return TelegramBot


async def return_streaming_bot(bot):
    global _bot_queue, _child_queues, _current_child_queue
    if _bot_queue is None:
        await populate_bot_queue()

    try:
        if _bot_queue.qsize() < (1 + len(_streaming_bots)):
            await _bot_queue.put(bot)
            logger.debug("Bot returned to main queue")
            return

        target_child = _current_child_queue % 5
        await _child_queues[target_child].put(bot)
        _current_child_queue = (target_child + 1) % 5
        logger.debug("Bot returned to child queue %s", target_child + 1)

    except Exception as e:
        logger.error("Error returning bot to queues: %s", e)


async def start_streaming_bots():
    for i, bot in enumerate(_streaming_bots):
        try:
            await bot.start(bot_token=bot._token)
            me = await bot.get_me()
            bot_uname = "@" + me.username
            logger.info("Streaming bot %s started successfully", bot_uname)
        except Exception as e:
            logger.error("Failed to start streaming bot %s: %s", bot_uname, e)

    await populate_bot_queue()


initialize_streaming_bots()
