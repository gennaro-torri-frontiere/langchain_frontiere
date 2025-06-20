import inspect
from langchain_community.document_loaders.base import BaseLoader

def list_implementations() -> list:
    return [
        name for name, func in globals().items()
        if inspect.isfunction(func) and name != "list_implementations"
    ]

def document_loader(path) -> BaseLoader:
    from langchain_community.document_loaders import DirectoryLoader
    return DirectoryLoader(path=path)   
