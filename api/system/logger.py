import os
import logging

from logging import FileHandler
from logging import Formatter
from logging import Filter
from logging.handlers import SMTPHandler
from api.providers.configuration.configuration_provider import ConfigurationProvider

config = ConfigurationProvider()

LOG_FORMAT = ("%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d")

class DbgFilter(Filter):
    def filter(self, rec):
        return rec.levelno == logging.DEBUG

ilogger = logging.getLogger("api")
ilogger.setLevel(logging.DEBUG)

ih = FileHandler("/var/log/uwsgi/espa-api-info.log")
dh = FileHandler("/var/log/uwsgi/espa-api-debug.log")
eh = SMTPHandler(mailhost='localhost', fromaddr=config.get('apiemailsender'), toaddrs=config.get('apiemailreceive').split(','), subject='ESPA API ERROR')

ih.setLevel(logging.INFO)
dh.setLevel(logging.DEBUG)
eh.setLevel(logging.DEBUG)

for handler in [ih, dh, eh]:
    ilogger.addHandler(handler)

    if isinstance(handler, logging.FileHandler):
        handler.setFormatter(Formatter(LOG_FORMAT))

    if handler.level == logging.DEBUG:
        handler.addFilter(DbgFilter())

