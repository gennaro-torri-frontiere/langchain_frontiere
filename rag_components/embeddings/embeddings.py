import inspect
from langchain_core.embeddings import Embeddings

def list_implementations() -> list:
    return [
        name for name, func in globals().items()
        if inspect.isfunction(func) and name != "list_implementations"
    ]

def bge_small() -> Embeddings:
    from langchain.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")