import logging
from datetime import datetime

from .vlr import VLRParser, VLRSession, VLRHandler

__all__ = ["VLRParser", "VLRSession", "VLRHandler"]

logging_level = logging.DEBUG

logFormatter = logging.Formatter(
    "%(asctime)s [%(levelname)-5.5s] [%(filename)s:%(lineno)d] %(message)s"
)
rootLogger = logging.getLogger()
rootLogger.setLevel(logging_level)

time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
fileHandler = logging.FileHandler(f"logs/{time_string}.log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
