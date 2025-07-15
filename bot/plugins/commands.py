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


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/start$"))
@verify_user(private=True)
async def welcome(event: NewMessage.Event | Message):
    id = event.sender_id
    user_name = "@" + event.sender.username if event.sender.username else None
    await add_user(id, user_name)

    await event.reply(
        message=static.WelcomeText % {"first_name": event.sender.first_name},
        buttons=[
            [
                Button.url(text="🔔 Update Channel", url="https://t.me/ELUpdates"),
                Button.url(text="👥 Support Group", url="https://t.me/ELSupport"),
            ]
        ],
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
