import os
import logging

from logging import FileHandler
from logging import Formatter
from logging import Filter
from logging.handlers import SMTPHandler
from api.utils import api_cfg

if not os.path.exists("logs"):
    os.mkdir("logs")

cfg = api_cfg()

LOG_FORMAT = ("%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d")

class DbgFilter(Filter):
    def filter(self, rec):
        return rec.levelno == logging.DEBUG

api_logger = logging.getLogger("api")
api_logger.setLevel(logging.DEBUG)

ih = FileHandler("logs/api-info.log")
dh = FileHandler("logs/api-debug.log")
eh = SMTPHandler(mailhost='localhost', fromaddr=cfg['apiemailsender'], toaddrs=cfg['apiemailreceive'].split(','), subject='ESPA API ERROR')

ih.setLevel(logging.INFO)
dh.setLevel(logging.DEBUG)
eh.setLevel(logging.DEBUG)

for handler in [ih, dh, eh]:
    api_logger.addHandler(handler)

    if isinstance(handler, logging.FileHandler):
        handler.setFormatter(Formatter(LOG_FORMAT))

    if handler.level == logging.DEBUG:
        handler.addFilter(DbgFilter())

