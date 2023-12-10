import asyncio
import aiohttp
from bot.config import Util, Server 
from logging import getLogger

logger = getLogger("ping")

async def ping_server():
    sleep_time = Util.PING_INTERVAL
    logger.info("Started with {}s interval between pings".format(sleep_time))
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(Server.BASE_URL) as resp:
                    logger.info("Pinged server with response: {}".format(resp.status))
        except TimeoutError:
            logger.warning("Couldn't connect to the site URL..")
        except Exception:
            logger.error("Unexpected error: ", exc_info=True)