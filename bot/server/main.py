from quart import Blueprint, Response, request, redirect
from .error import abort
from bot import get_streaming_bot, return_streaming_bot, logger
from bot.config import Telegram
from math import ceil, floor
from bot.modules.telegram import get_file_properties

bp = Blueprint("main", __name__)


@bp.route("/")
async def home():
    return redirect(f"https://t.me/{Telegram.BOT_USERNAME}")


@bp.route("/dl/<int:file_id>")
async def transmit_file(file_id):
    selected_bot = await get_streaming_bot()
    me = await selected_bot.get_me()
    bot_name = "@" + me.username

    logger.info("File download request - File ID: %s, Using bot: %s", file_id, bot_name)

    file = None
    try:
        file = await selected_bot.get_messages(Telegram.CHANNEL_ID, ids=int(file_id))
        if file:
            logger.info(
                "Message retrieved successfully from channel %s using bot: %s",
                Telegram.CHANNEL_ID,
                bot_name,
            )
        else:
            logger.warning(
                "Message %s not found in channel %s", file_id, Telegram.CHANNEL_ID
            )
            await return_streaming_bot(selected_bot)
            abort(404)
    except Exception as e:
        logger.error(
            "Failed to retrieve message %s using bot %s: %s", file_id, bot_name, e
        )
        await return_streaming_bot(selected_bot)
        abort(500)

    code = request.args.get("code") or abort(401)
    range_header = request.headers.get("Range", 0)

    if code != file.raw_text:
        logger.warning("Access denied - Invalid code for file %s", file_id)
        await return_streaming_bot(selected_bot)
        abort(403)

    file_name, file_size, mime_type = get_file_properties(file)
    logger.info(
        "File properties - Name: %s, Size: %s, Type: %s",
        file_name,
        file_size,
        mime_type,
    )

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
        logger.info(
            "Range request - Bytes: %s-%s/%s", from_bytes, until_bytes, file_size
        )
    else:
        from_bytes = 0
        until_bytes = file_size - 1
        logger.info("Full file request - Size: %s bytes", file_size)

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        logger.error(
            "Invalid range request - Bytes: %s-%s/%s",
            from_bytes,
            until_bytes,
            file_size,
        )
        await return_streaming_bot(selected_bot)
        abort(416, "Invalid range.")

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = ceil(until_bytes / chunk_size) - floor(offset / chunk_size)

    headers = {
        "Content-Type": f"{mime_type}",
        "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
        "Content-Length": str(req_length),
        "Content-Disposition": f'attachment; filename="{file_name}"',
        "Accept-Ranges": "bytes",
    }

    logger.info(
        "Starting file stream - Bot: %s, Chunks: %s, Chunk size: %s",
        bot_name,
        part_count,
        chunk_size,
    )

    async def file_generator():
        current_part = 1
        try:
            async for chunk in selected_bot.iter_download(
                file,
                offset=offset,
                chunk_size=chunk_size,
                stride=chunk_size,
                file_size=file_size,
            ):
                if not chunk:
                    break
                elif part_count == 1:
                    yield chunk[first_part_cut:last_part_cut]
                elif current_part == 1:
                    yield chunk[first_part_cut:]
                elif current_part == part_count:
                    yield chunk[:last_part_cut]
                else:
                    yield chunk

                current_part += 1

                if current_part > part_count:
                    break

            logger.info(
                "File stream completed successfully - File: %s, Bot: %s",
                file_name,
                bot_name,
            )

        except Exception as e:
            logger.error(
                "Error during file streaming - File: %s, Bot: %s, Error: %s",
                file_name,
                bot_name,
                e,
            )
            raise
        finally:
            await return_streaming_bot(selected_bot)
            logger.info("Bot %s returned to queue", bot_name)

    return Response(
        file_generator(), headers=headers, status=206 if range_header else 200
    )


# @bp.route("/stream/<int:file_id>")
# async def stream_file(file_id):
#     code = request.args.get("code") or abort(401)

#     return await render_template(
#         "player.html", mediaLink=f"{Server.BASE_URL}/dl/{file_id}?code={code}"
#     )


# @bp.route("/file/<int:file_id>")
# async def file_deeplink(file_id):
#     code = request.args.get("code") or abort(401)

#     return redirect(f"https://t.me/{Telegram.BOT_USERNAME}?start=file_{file_id}_{code}")
