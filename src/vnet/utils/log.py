"""
Configure tracing net logging settings.
"""
from logging import getLogger, Logger, DEBUG, INFO, StreamHandler, Formatter, handlers, setLoggerClass
import datetime


def setup_log_handler(log_handler=None):
    """set log formatter and file handler"""
    if log_handler:
        return log_handler
    else:
        formatter = Formatter(
            "%(asctime)s | %(process)d | %(name)s, %(funcName)s, %(lineno)d | %(levelname)s | %(message)s")
        # stream_handler = StreamHandler()
        # stream_handler.setLevel(DEBUG)
        # stream_handler.setFormatter(formatter)
        # logger.addHandler(stream_handler)
        filename = "vnet-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用
        file_handler = handlers.RotatingFileHandler(filename="log/" + filename,
                                                    maxBytes=16777216,
                                                    backupCount=2)
        file_handler.setLevel(DEBUG)
        file_handler.setFormatter(formatter)
        return file_handler


def setup_tracingnet_logger(log_level=INFO, log_handler=None):
    """set up logger in 'vnet'"""
    setLoggerClass(Logger)
    logger = getLogger('vnet')
    logger.setLevel(log_level)
    handler = setup_log_handler(log_handler=log_handler)
    if handler:
        logger.addHandler(handler)