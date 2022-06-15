import sys
import logging
import traceback
import common.logs


def log(func):
    def wrapper(*args, **kwargs):
        logger_name = 'parser'
        LOGGER = logging.getLogger(logger_name)

        res = func(*args, **kwargs)
        LOGGER.debug(f'Вызов функции {func.__name__} c параметрами {args}, {kwargs}.'
                     f'Вызов из модуля {func.__module__}.'
                     f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.')
        return res
    return wrapper
