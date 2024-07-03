from telethon.events import NewMessage
from telethon.tl.custom import Message
from bot import TelegramBot
from bot.db.ban_sql import is_banned, ban_user, unban_user
from bot.config import Telegram


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/ban\s\d+$"))
async def banuser(event: NewMessage.Event | Message):
    user_id = str(event.sender_id)
    if user_id not in str(Telegram.OWNER_ID):
        return
    data = event.text.split()
    if len(data) == 2:
        user_id = data[-1]
        banned = await is_banned(int(user_id))
        if not banned:
            await ban_user(int(user_id))
            await event.reply(f"User {user_id} banned")
        else:
            await event.reply(f"User {user_id} is already banned")

    else:
        await event.reply("Please send in proper format `/ban user_id`")


@TelegramBot.on(NewMessage(incoming=True, pattern=r"^/unban\s\d+$"))
async def unbanuser(event: NewMessage.Event | Message):
    user_id = str(event.sender_id)
    if user_id not in str(Telegram.OWNER_ID):
        return
    data = event.text.split()
    if len(data) == 2:
        user_id = data[-1]
        banned = await is_banned(int(user_id))
        if banned:
            await unban_user(int(user_id))
            await event.reply(f"User {user_id} unbanned")
        else:
            await event.reply(f"User {user_id} is not in ban list")
    else:
        await event.reply("Please send in proper format `/unban user_id`")
