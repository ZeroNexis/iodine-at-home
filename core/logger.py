import os
import sys
from pathlib import Path
from loguru import logger as Logger

basic_logger_format = (
    "<green>[{time:HH:mm:ss}]</green><level>[{level}] {message}</level>"
)
logfile_logger_format = "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> <level>[{level}]<yellow>[{name}:{function}:{line}]</yellow>: {message}</level>"


class LoggingLogger:

    def __init__(self):
        self.log = Logger
        self.log.remove()
        self.log.add(
            sys.stderr, format=basic_logger_format, level="DEBUG", colorize=True
        )
        self.cur_handler = None
        self.log.add(
            Path("./logs/{time:YYYY-MM-DD}.log"),
            format=logfile_logger_format,
            retention="10 days",
            encoding="utf-8",
        )
        self.info = self.log.info
        self.debug = self.log.debug
        self.warning = self.log.warning
        self.error = self.log.error
        self.success = self.log.success
    
    def clear(self):
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

logger = LoggingLogger()
