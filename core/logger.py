import logging
from logging.handlers import RotatingFileHandler
import os

LOG_PATH = "log/app.log"
os.makedirs("log", exist_ok=True)

logger = logging.getLogger("KONE")
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    LOG_PATH, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
