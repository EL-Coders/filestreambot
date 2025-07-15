import os
import sys
from logging import getLogger
from bot.config import Util
import asyncio

logger = getLogger("restarter")


async def restart_bot():
    restart_interval = Util.RSTRT_INTERVAL
    logger.info("Started with %ss interval between restarts", restart_interval)
    while True:
        await asyncio.sleep(restart_interval)
        logger.warning("Scheduled restart initiated")
        os.execv(sys.executable, ["python3", "-m", "bot"] + sys.argv)
