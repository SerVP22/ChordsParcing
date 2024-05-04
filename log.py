from loguru import logger

def level_filter(level):
    def is_level(record):
        return record["level"].name == level
    return is_level

logger.add("logs/info/info_{time}.log", format="{time} | {level} | {message}", filter=level_filter(level="INFO"))
logger.add("logs/errors/errors_{time}.log", format="{time} | {level} | {message}", filter=level_filter(level="ERROR"))

# for i in range(3):
#     #logger.debug(f"It is a {i} line from debug")
#     logger.info(f"It is a {i} line from info")
#     logger.error(f"It is a {i} line from error")
"""
logger.info(f"App is get response: {req}")
logger.error(f"App is get Exception: {msg}")

"""