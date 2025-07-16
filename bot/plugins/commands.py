import os
import sys
import asyncio
from telethon import Button
from telethon.events import NewMessage
from telethon.tl.custom.message import Message
from bot import TelegramBot
from bot.config import Telegram
from bot.modules import static
from bot.modules.decorators import verify_user
from bot.db.sql import add_user
from bot.db.stats_sql import get_formatted_stats


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/start$"))
@verify_user(private=True)
async def welcome(event: NewMessage.Event | Message):
    id = event.sender_id
    user_name = "@" + event.sender.username if event.sender.username else None
    await add_user(id, user_name)

    try:
        stats = await get_formatted_stats()
        stats_text = (
            f"\n**📊 Statistics:**\n"
            f"**Today:** `{stats['today_files']} files - {stats['today_size']}`\n"
            f"**Yesterday:** `{stats['yesterday_files']} files - {stats['yesterday_size']}`\n"
            f"**Last 7 days:** `{stats['week_files']} files - {stats['week_size']}`\n\n"
            f"Send /filestats to get more detailed statistics"
        )
    except Exception:
        stats_text = ""

    await event.reply(
        message=static.WelcomeText % {"first_name": event.sender.first_name} + stats_text,
        buttons=[
            [
                Button.url(text="🔔 Update Channel", url="https://t.me/ELUpdates"),
                Button.url(text="👥 Support Group", url="https://t.me/ELSupport"),
            ]
        ],
    )


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/filestats$"))
@verify_user(private=True)
async def file_statistics(event: NewMessage.Event | Message):
    try:
        stats = await get_formatted_stats()
        
        stats_message = f"""**📊 File Statistics**

**📅 Today:**
• Files: `{stats['today_files']}`
• Size: `{stats['today_size']}`

**📅 Yesterday:**
• Files: `{stats['yesterday_files']}`
• Size: `{stats['yesterday_size']}`

**📅 Last 7 Days:**
• Files: `{stats['week_files']}`
• Size: `{stats['week_size']}`

**📈 All Time:**
• Total Files: `{stats['total_files']}`
• Total Size: `{stats['total_size']}`

**@ELUpdates**
"""

        await event.reply(stats_message)
        
    except Exception as e:
        await event.reply(
            "❌ Error retrieving statistics. Please try again later. Error: %s", e
        )


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/help$"))
@verify_user(private=True)
async def help_text(event: NewMessage.Event | Message):
    await event.reply(
        message=static.HelpText,
    )


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/info$"))
@verify_user(private=True)
async def user_info(event: Message):
    await event.reply(static.UserInfoText.format(sender=event.sender))


@TelegramBot.on(NewMessage(chats=Telegram.OWNER_ID, incoming=True, pattern=r"^/logs$"))
async def send_log(event: NewMessage.Event | Message):
    mess = await event.reply("Sending logs...")
    await event.reply(file="event-log.txt")
    await mess.delete()


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/restart$"))
async def restart(event: NewMessage.Event | Message):
    mess = await event.reply("Restarting...")
    await asyncio.sleep(2)
    await mess.edit("Restart completed.. initializing...")
    os.execv(sys.executable, ["python3", "-m", "bot"] + sys.argv)
