import os
import sys
from logging import getLogger
import asyncio

logger = getLogger("restarter")


async def restart_bot():
    while True:
        await asyncio.sleep(60 * 60)
        logger.warning("Scheduled restart initiated")
        os.execv(sys.executable, ["python3", "-m", "bot"] + sys.argv)
