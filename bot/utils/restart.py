import os
import sys
from logging import getLogger
from bot.config import Util
import asyncio

logger = getLogger("restarter")


async def restart_bot():
    while True:
        await asyncio.sleep(Util.RSTRT_INTERVAL)
        logger.warning("Scheduled restart initiated")
        os.execv(sys.executable, ["python3", "-m", "bot"] + sys.argv)
