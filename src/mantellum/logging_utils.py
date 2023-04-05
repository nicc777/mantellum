import os
import logging
from logging.handlers import TimedRotatingFileHandler


class LoggingImpl:

    def __init__(self):
        self.logger = None


def _get_final_logging_level(force_debug: bool=False):
    if force_debug is True:
        return logging.DEBUG
    try:
        if bool(int(os.getenv('DEBUG', '0'))) is True:
            return logging.DEBUG
    except:
        pass
    return logging.INFO


def set_logger(custom_name: str=None, force_debug: bool=False)->logging.Logger:
    final_logging_level = _get_final_logging_level(force_debug=force_debug)
    script_name = os.path.basename(__file__)
    script_name = script_name.replace('.py', '')
    if custom_name is not None:
        script_name = custom_name
    logger = logging.getLogger(script_name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d -  %(message)s')
    lh = TimedRotatingFileHandler('{}.log'.format(script_name), when="midnight", interval=1, backupCount=5)
    lh.setLevel(final_logging_level)
    lh.setFormatter(formatter)
    logger.addHandler(lh)
    logger.setLevel(final_logging_level)
    logger.info('STARTING')
    logger.debug('DEBUG enabled')
    packaged_logger.logger = logger


packaged_logger = LoggingImpl()
set_logger(custom_name=None, force_debug=False)


def set_custom_logger(logger: logging.Logger):
    packaged_logger.logger = logger


def get_logger()->logging.Logger:
    return packaged_logger.logger



