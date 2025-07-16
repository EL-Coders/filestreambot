from logging import getLogger
from secrets import token_hex
from random import choice

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
from bot.modules import static
from bot.modules.telegram import filter_files, send_message
from bot.db.ban_sql import is_banned
from bot.db.stats_sql import add_file_size

logger = getLogger("fileserve")


def get_WORKERS_URL(message_id: int, secret_code: str, user_id: int) -> list[str]:
    WORKERS_URLs = []
    if Server.WORKERS_URL:
        url1 = f"{Server.WORKERS_URL}/dl/{message_id}?code={secret_code}-{user_id}"
        WORKERS_URLs.append(url1)
    if Server.WORKERS_URL_2:
        url2 = f"{Server.WORKERS_URL_2}/dl/{message_id}?code={secret_code}-{user_id}"
        WORKERS_URLs.append(url2)
    if Server.WORKERS_URL_3:
        url3 = f"{Server.WORKERS_URL_3}/dl/{message_id}?code={secret_code}-{user_id}"
        WORKERS_URLs.append(url3)
    return WORKERS_URLs


@TelegramBot.on(NewMessage(incoming=True, func=filter_files))
@verify_user(private=True)
async def user_file_handler(event: NewMessage.Event | Message):
    user_id = event.sender_id
    secret_code = token_hex(Telegram.SECRET_CODE_LENGTH)
    event.message.text = f"`{secret_code}`-`{user_id}`"
    message = await send_message(event.message)
    message_id = message.id

    try:
        file_size = 0
        if hasattr(event.message, 'file') and event.message.file:
            file_size = event.message.file.size or 0
        if file_size > 0:
            await add_file_size(file_size)
            logger.info("File size tracked: %s bytes for user %s", file_size, user_id)
        else:
            logger.warning("Could not determine file size for user %s", user_id)
    except Exception as e:
        logger.error("Error tracking file size: %s", e)

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

    WORKERS_URLs = get_WORKERS_URL(message_id, secret_code, user_id)
    dl_link = f"{Server.BASE_URL}/dl/{message_id}?code={secret_code}-{user_id}"
    # tg_link = f"{Server.BASE_URL}/file/{message_id}?code={secret_code}-{user_id}"
    if WORKERS_URLs:
        wr_link = choice(WORKERS_URLs)

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
    kb = [
            [
                Button.url("📩 Download", dl_link),
            ],
            
        ]
    if WORKERS_URLs:
        kb.append([Button.url("🚀 Fast Download", wr_link)])
        mess = f"**Download Links:**\n\n**📩 Download Link:** `{dl_link}`\n\n**🚀 Fast Download Link:** `{wr_link}`\n\n▸ __You can copy paste the link in any streaming supported media player & stream__\n▸ __Use normal download link if fast link is not working__\n**@ELUpdates**"
    else:
        mess = f"**Download Links:**\n\n**📩 Download Link:** `{dl_link}`\n\n▸ __You can copy paste the link in any streaming supported media player & stream__"
        
    kb.append([Button.inline("❌ Revoke", f"rm_{message_id}_{secret_code}")])
    
        
    await event.reply(
        message=mess,
        buttons=kb,
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
