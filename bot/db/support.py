import asyncio
from telethon.errors import FloodWaitError
from bot import TelegramBot, logger
from bot.db.sql import del_user, query_msg


async def users_info():
    active = 0
    blocked = 0
    identity = await query_msg()

    for user_id in identity:
        typing_successful = False
        try:
            async with TelegramBot.action(int(user_id[0]), "typing"):
                await asyncio.sleep(0.1)
                typing_successful = True
        except FloodWaitError as e:
            logger.info("Floodwait while broadcast, sleeping %s", user_id)
            await asyncio.sleep(e.seconds)
        except Exception:
            typing_successful = False
            await del_user(user_id)
            logger.info("Deleted user id %s from broadcast list", user_id)

        if typing_successful:
            active += 1
        else:
            blocked += 1

    return active, blocked
