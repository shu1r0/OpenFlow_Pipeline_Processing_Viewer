from logging import getLogger, Logger, DEBUG, INFO, StreamHandler, Formatter, handlers, setLoggerClass
import datetime


def get_log_handler(file_path):
    formatter = Formatter(
        "%(asctime)s | %(process)d | %(name)s, %(funcName)s, %(lineno)d | %(levelname)s | %(message)s")
    # stream_handler = StreamHandler()
    # stream_handler.setLevel(DEBUG)
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(stream_handler)
    file_handler = handlers.RotatingFileHandler(filename=file_path,
                                                maxBytes=16777216,
                                                backupCount=2)
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(formatter)
    return file_handler


def setup_logger(log_level=INFO, log_handler=None):
    setLoggerClass(Logger)
    logger = getLogger('tracing_of_pipeline')
    logger.setLevel(log_level)
    if log_handler:
        logger.addHandler(log_handler)
