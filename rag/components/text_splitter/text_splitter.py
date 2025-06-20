import inspect
from langchain_text_splitters.base import TextSplitter

def list_implementations() -> list:
    return [
        name for name, func in globals().items()
        if inspect.isfunction(func) and name != "list_implementations"
    ]

def recursive_character_text_splitter(chunk_size: int, chunk_overlap: int) -> TextSplitter:
    """
    class: RecursiveCharacterTextSplitter
    Splits text into chunks based on character length, recursively splitting larger chunks.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )