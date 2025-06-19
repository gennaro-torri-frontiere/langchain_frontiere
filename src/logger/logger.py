import os
import logging
from typing import Optional


class Logger:
    _instance = None

    def __new__(cls, file_log: Optional[str] = None, logger_name: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_log: Optional[str] = None, logger_name: Optional[str] = None):
        handlers = [logging.StreamHandler()]
        if file_log:
            handlers.append(logging.FileHandler(file_log))

        logging.basicConfig(
            level="INFO",
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            handlers=handlers
        )
        self.__logger = logging.getLogger(logger_name)

    @property
    def logger(self) -> logging.Logger:

        return self.__logger


def get_logger():
    return Logger(file_log=os.getenv('LOGFILE')).logger
