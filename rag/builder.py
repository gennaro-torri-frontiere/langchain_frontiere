from importlib import import_module
from typing import Callable
from src.utils import load_config
from src.logger import get_logger

from rag.base.RAGBase import RAGBase

class Builder:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Builder, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.logger = get_logger()
        self.types_rag = {
            "base": RAGBase
        }
        self.rags = {}

    def get_rag(self, name: str, type: str, config_path: str):
        if type not in self.types_rag:
            raise ValueError(f"RAG type {type} is not supported. Available types: {self.types_rag.keys()}")
        
        if name not in self.rags:
            self.logger.info(f"Creating RAG instance: {name} of type {type}")
            config: dict = load_config(config_path)
            class_rag = self.types_rag[type] 
            istance_rag = class_rag(name=name, config=config)
            self.rags[name] = istance_rag
        
        self.logger.info(f"Returning RAG instance: {name} of type {type}")
        return self.rags[name]