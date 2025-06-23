from langchain_text_splitters import RecursiveCharacterTextSplitter


def recursive_character_text_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    """
    Splits text into chunks based on character length, recursively splitting larger chunks.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )