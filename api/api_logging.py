import os
import logging

from logging import FileHandler
from logging import Formatter
from logging.handlers import SMTPHandler
from api.utils import api_cfg

if not os.path.exists("logs"):
    os.mkdir("logs")

cfg = api_cfg()

LOG_FORMAT = ("%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d")

api_logger = logging.getLogger("api")
api_logger.setLevel(logging.DEBUG)

ih = FileHandler("logs/api-info.log")
dh = FileHandler("logs/api-debug.log")
eh = SMTPHandler(mailhost='localhost', fromaddr=cfg['apiemailsender'], toaddrs=cfg['apiemailreceive'].split(','), subject='API ERROR')

ih.setLevel(logging.WARN)
dh.setLevel(logging.DEBUG)
eh.setLevel(logging.DEBUG)

ih.setFormatter(Formatter(LOG_FORMAT))
dh.setFormatter(Formatter(LOG_FORMAT))

api_logger.addHandler(ih)
api_logger.addHandler(dh)
api_logger.addHandler(eh)
