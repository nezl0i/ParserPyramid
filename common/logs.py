import logging.handlers
import os


LOGGING_LEVEL = logging.DEBUG
SERVER_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s [%(module)s]  - %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'parser.log')

# Потоки
STEAM_HANDLER = logging.StreamHandler()
STEAM_HANDLER.setFormatter(SERVER_FORMATTER)
STEAM_HANDLER.setLevel(logging.ERROR)

FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', when='d', interval=1)
FILE_HANDLER.suffix = '%d-%m-%Y'
FILE_HANDLER.setFormatter(SERVER_FORMATTER)

# Регистратор
LOGGER = logging.getLogger('parser')
LOGGER.addHandler(STEAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.warning('Предупреждение')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')

