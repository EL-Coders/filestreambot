from functools import wraps
from typing import Callable

from telethon.events import CallbackQuery, NewMessage

from bot.config import Telegram


def verify_user(private: bool = False):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update: NewMessage.Event | CallbackQuery.Event):
            if private and not update.is_private:
                return

            chat_id = str(update.chat_id)

            if not Telegram.ALLOWED_USER_IDS or chat_id in Telegram.ALLOWED_USER_IDS:
                return await func(update)

        return wrapper

    return decorator
