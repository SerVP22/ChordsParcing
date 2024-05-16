import loguru
from loguru import logger

def level_filter(level):
    def is_level(record):
        return record["level"].name == level
    return is_level

logger.add("logs/info/info_{time}.log",
           format="{time} | {level} | {message}",
           filter=level_filter(level="INFO"),
           # rotation="callable"
           )
logger.id_error = logger.add("logs/errors/errors_{time}.log",
                             format="{time} | {level} | {message}",
                             filter=level_filter(level="ERROR"))
