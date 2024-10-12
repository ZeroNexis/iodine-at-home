import sys
import core
from core.logger import logger
import asyncio

py_version = sys.version_info

if py_version < (3, 11):
    logger.info(
        f"你使用的 Python 版本是 {py_version[0]}.{py_version[1]}.{py_version[2]}，",
    )
    logger.info("而该程序要求使用 3.11 版本及以上的 Python，请及时更换。")
    sys.exit(1)


core.init()  # 初始化