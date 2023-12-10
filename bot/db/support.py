import asyncio
from bot.db.sql import query_msg
from telethon.errors import FloodWaitError
from telethon import events
from bot import TelegramBot


async def users_info():
    active = 0
    blocked = 0
    identity = await query_msg()

    for user_id in identity:
        typing_successful = False
        try:
            async with TelegramBot.action(int(user_id[0]), 'typing'):
                await asyncio.sleep(0.1)
                typing_successful = True
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            typing_successful = False

        if typing_successful:
            active += 1
        else:
            blocked += 1

    return active, blocked