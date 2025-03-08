from logging import getLogger
from secrets import token_hex

from telethon import Button
from telethon.errors import (
    MessageAuthorRequiredError,
    MessageIdInvalidError,
    MessageNotModifiedError,
)
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.events import NewMessage
from telethon.tl.custom import Message

from bot import TelegramBot
from bot.config import Server, Telegram, Util
from bot.modules.decorators import verify_user
from bot.modules.static import *
from bot.modules.telegram import filter_files, send_message
from bot.db.ban_sql import is_banned

logger = getLogger("fileserve")


@TelegramBot.on(NewMessage(incoming=True, func=filter_files))
@verify_user(private=True)
async def user_file_handler(event: NewMessage.Event | Message):
    user_id = event.sender_id
    secret_code = token_hex(Telegram.SECRET_CODE_LENGTH)
    event.message.text = f"`{secret_code}`"
    message = await send_message(event.message)
    await TelegramBot.send_message(
        entity=Telegram.CHANNEL_ID, message=f"User ID: `{user_id}`"
    )
    message_id = message.id

    if await is_banned(user_id):
        await event.reply("You are banned. You can't use this bot.")
        return

    force_sub = Util.SUB_CHANNEL
    if force_sub:
        try:
            user = await TelegramBot.get_permissions(force_sub, user_id)
            if user.is_banned:
                await event.reply("Sorry, you are BANNED to use me.")
                return
        except UserNotParticipantError:
            link = Util.SUB_CHANNEL_LINK
            await event.reply(
                message="Please join my Updates Channel to use this bot!",
                buttons=[
                    [
                        Button.url("🤖 Join Channel", link),
                    ],
                ],
            )
            return
        except Exception as e:
            logger.warning(e)
            await event.reply(
                message="Something went wrong, please contact my support group",
            )
            return

    dl_link = f"{Server.BASE_URL}/dl/{message_id}?code={secret_code}"
    tg_link = f"{Server.BASE_URL}/file/{message_id}?code={secret_code}"
    # deep_link = (
    #     f"https://t.me/{Telegram.BOT_USERNAME}?start=file_{message_id}_{secret_code}"
    # )

    # if (event.document and "video" in event.document.mime_type) or event.video:
    #     stream_link = f"{Server.BASE_URL}/stream/{message_id}?code={secret_code}"
    #     await event.reply(
    #         message=MediaLinksText
    #         % {
    #             "dl_link": dl_link,
    #             "tg_link": tg_link,
    #             "stream_link": stream_link,
    #         },
    #         buttons=[
    #             [Button.url("Download", dl_link), Button.url("Stream", stream_link)],
    #             [
    #                 Button.inline("Revoke", f"rm_{message_id}_{secret_code}"),
    #             ],
    #         ],
    #     )
    # else:
    await event.reply(
        message=FileLinksText % {"dl_link": dl_link, "tg_link": tg_link},
        buttons=[
            [
                Button.url("Download", dl_link),
            ],
            [Button.inline("Revoke", f"rm_{message_id}_{secret_code}")],
        ],
    )


# @TelegramBot.on(NewMessage(incoming=True, func=filter_files, forwards=False))
# @verify_user()
# async def channel_file_handler(event: NewMessage.Event | Message):
#     secret_code = token_hex(Telegram.SECRET_CODE_LENGTH)
#     event.message.text = f"`{secret_code}`"
#     message = await send_message(event.message)
#     message_id = message.id

#     dl_link = f"{Server.BASE_URL}/dl/{message_id}?code={secret_code}"
#     tg_link = f"{Server.BASE_URL}/file/{message_id}?code={secret_code}"

#     if (event.document and "video" in event.document.mime_type) or event.video:
#         stream_link = f"{Server.BASE_URL}/stream/{message_id}?code={secret_code}"

#         try:
#             await event.edit(
#                 buttons=[
#                     [
#                         Button.url("Download", dl_link),
#                         Button.url("Stream", stream_link),
#                     ],
#                     [Button.url("Get File", tg_link)],
#                 ]
#             )
#         except (
#             MessageAuthorRequiredError,
#             MessageIdInvalidError,
#             MessageNotModifiedError,
#         ):
#             pass
#     else:
#         try:
#             await event.edit(
#                 buttons=[
#                     [Button.url("Download", dl_link), Button.url("Get File", tg_link)]
#                 ]
#             )
#         except (
#             MessageAuthorRequiredError,
#             MessageIdInvalidError,
#             MessageNotModifiedError,
#         ):
#             pass
