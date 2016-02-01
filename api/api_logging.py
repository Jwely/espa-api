import logging

from logging import FileHandler
from logging import Formatter

LOG_FORMAT = ("%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d")

info_logger = logging.getLogger("api.info")
debug_logger = logging.getLogger("api.debug")

info_logger.setLevel(logging.DEBUG)
debug_logger.setLevel(logging.DEBUG)

info_logger_file_handler = FileHandler("logs/api-info.log")
debug_logger_file_handler = FileHandler("logs/api-debug.log")

#info_logger_file_handler.setLevel(INFO_LOG_LEVEL)
#debug_logger_file_handler.setLevel(WARN_LOG_LEVEL)

info_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
debug_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))

info_logger.addHandler(info_logger_file_handler)
debug_logger.addHandler(debug_logger_file_handler)


