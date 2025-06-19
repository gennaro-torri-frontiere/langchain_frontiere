from src.utils import load_config
from src.logger import get_logger

LOGGER = get_logger()

class Builder:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Builder, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        if not hasattr(self, '_initialized'):
            self.config = config
            self._initialized = True