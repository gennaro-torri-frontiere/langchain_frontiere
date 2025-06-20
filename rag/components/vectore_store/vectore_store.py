import inspect
from rag.components.embeddings import embeddings
from langchain.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings


def list_implementations() -> list:
    return [
        name for name, func in globals().items()
        if inspect.isfunction(func) and name != "list_implementations"
    ]

def chroma(collection_name: str, host_client: str, port_client: str, embeddings_name: str, embeddings_params: dict = {}) -> VectorStore:
    """
    class: Chroma
    istanziata con un client HTTP per ChromaDB e una funzione di embedding specificata.
    """
    import chromadb
    from langchain.vectorstores import Chroma

    if embeddings_name not in embeddings.list_implementations():
        raise ValueError(f"Embedding {embeddings_name} is not supported. Available embeddings: {embeddings.list_implementations()}")
    else:
        embedding_function = getattr(embeddings, embeddings_name)(**embeddings_params)

    return Chroma(
        embedding_function=embedding_function,
        collection_name=collection_name,
        client=chromadb.HttpClient(
            host=host_client, 
            port=port_client
        )
    )