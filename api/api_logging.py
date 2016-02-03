import os
import logging

from logging import FileHandler
from logging import Formatter

if not os.path.exists("logs"):
    os.mkdir("logs")

LOG_FORMAT = ("%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d")

api_logger = logging.getLogger("api")
api_logger.setLevel(logging.DEBUG)

ih = FileHandler("logs/api-info.log")
dh = FileHandler("logs/api-debug.log")

ih.setLevel(logging.WARN)
dh.setLevel(logging.DEBUG)

ih.setFormatter(Formatter(LOG_FORMAT))
dh.setFormatter(Formatter(LOG_FORMAT))

api_logger.addHandler(ih)
api_logger.addHandler(dh)

