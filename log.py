import loguru
from loguru import logger

class MyLogger():
    def __init__(self):
        self.logger = logger.add("logs/info/info_{time}.log",
                   format="{time} | {level} | {message}",
                   filter=self.level_filter(level="INFO"),
                   # rotation="callable"
                   )
        self.logger_error = logger.add("logs/errors/errors_{time}.log",
                                     format="{time} | {level} | {message}",
                                     filter=self.level_filter(level="ERROR"))

    def level_filter(self, level):
        def is_level(record):
            return record["level"].name == level
        return is_level


