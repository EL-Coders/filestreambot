import asyncio
import time
import datetime

from telethon.errors import FloodWaitError
from telethon.events import NewMessage
from telethon.tl.custom.message import Message

from bot import TelegramBot
from bot.config import Telegram
from bot.db.sql import query_msg
from bot.db.support import users_info


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/stats$"))
async def subscribers_count(event: NewMessage.Event | Message):
    user_id = str(event.sender_id)
    if user_id not in str(Telegram.OWNER_ID):
        return
    wait_msg = "__Calculating, please wait...__"
    msg = await event.reply(wait_msg)
    active, blocked = await users_info()
    stats_msg = f"**Stats**\nActive: `{active}`\nBlocked / Deleted: `{blocked}`"
    await msg.edit(stats_msg)


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/broadcast$"))
async def send_text(event: NewMessage.Event | Message):
    user_id = str(event.sender_id)
    if user_id not in str(Telegram.OWNER_ID):
        return

    if (
        (" " not in event.text)
        and ("broadcast" in event.text)
        and (event.message.reply_to is not None)
    ):
        start_time = time.time()
        success = 0
        failed = 0
        query = await query_msg()
        msg = await event.get_reply_message()
        for row in query:
            chat_id = int(row[0])
            try:
                await TelegramBot.send_message(chat_id, msg)
                success += 1
            except FloodWaitError as e:
                print("Floodwait while broadcasting, sleeping for %s", e.seconds)
                await asyncio.sleep(e.seconds)
                failed += 1
            except Exception as e:
                failed += 1
        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await event.reply(
            f"**Broadcast Completed**\nSent to: `{success}`\nFailed: `{failed}`\nCompleted in `{time_taken}` hh:mm:ss"
        )

    else:
        reply_error = (
            "`Use this command as a reply to any telegram message without any spaces.`"
        )
        msg = await event.reply(reply_error)
        await asyncio.sleep(8)
        await msg.delete()
