from core.logger import logger

class Mapper:
    def __init__(self):
        self.cache = {}

    def process(self, source, payload):
        logger.debug(f"Mapping from {source}")
        self.cache[source] = payload
        return self.cache
