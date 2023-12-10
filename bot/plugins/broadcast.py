#  !/usr/bin/env python3
#  -*- coding: utf-8 -*-
#  Name     : broadcast-bot [ Telegram ]
#  Repo     : https://github.com/m4mallu/broadcast-bot
#  Author   : Renjith Mangal [ https://t.me/space4renjith ]
#  Licence  : GPL-3

import os
import asyncio
# from pyrogram.types import Message
from bot import TelegramBot
from telethon.events import NewMessage
from telethon.tl.custom.message import Message
# from pyrogram import Client, filters
from telethon.errors import FloodWaitError
from bot.db.support import users_info
from bot.db.sql import add_user, query_msg
from bot.config import Telegram


# ------------------------------- View Subscribers --------------------------------- #
@TelegramBot.on(NewMessage(incoming=True, pattern=r'^/stats$'))
async def subscribers_count(event: NewMessage.Event | Message):
    id = str(event.sender_id)
    if id not in str(Telegram.OWNER_ID):
        return
    WAIT_MSG = "**Please Wait...**"
    msg = await event.reply(WAIT_MSG)
    messages = await users_info()
    active = messages[0]
    blocked = messages[1]
    # await m.delete()
    USERS_LIST = "**Total:**\n\nSubscribers - {}\nBlocked / Deleted - {}"
    await msg.edit(USERS_LIST.format(active, blocked))


# ------------------------ Send messages to subs ----------------------------- #
@TelegramBot.on(NewMessage(incoming=True, pattern=r'^/broadcast$'))
async def send_text(event: NewMessage.Event | Message):
    id = str(event.sender_id)
    if id not in str(Telegram.OWNER_ID):
        return
    if (" " not in event.text) and ("broadcast" in event.text) and (event.message.reply_to is not None):       
        query = await query_msg()
        msg = await event.get_reply_message()
        for row in query:
            chat_id = int(row[0])
            try:
                await TelegramBot.send_message(chat_id,msg)
            except FloodWaitError as e:
                await asyncio.sleep(e.x)
            except Exception as e:
                pass
    else:
        REPLY_ERROR = "`Use this command as a reply to any telegram message with out any spaces.`"
        msg = await event.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()