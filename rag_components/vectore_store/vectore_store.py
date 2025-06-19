import inspect
from rag_components.embeddings import embeddings
from langchain.vectorstores import VectorStore

def list_implementations() -> list:
    return [
        name for name, func in globals().items()
        if inspect.isfunction(func) and name != "list_implementations"
    ]

def chroma(collection_name: str, host_client: str, port_client: str, embeddings_name: str, embeddings_parmas: dict = {}) -> VectorStore:
    """
    class: Chroma
    istanziata con un client HTTP per ChromaDB e una funzione di embedding specificata.
    """
    import chromadb
    from langchain.vectorstores import Chroma

    if embeddings not in embeddings.list_embeddings().keys():
        raise ValueError(f"Embedding {embeddings} is not supported. Available embeddings: {embeddings.list_embeddings().keys()}")
    else:
        embedding_function = getattr(embeddings, embeddings_name)(**embeddings_parmas)

    return Chroma(
        embedding_function=embedding_function,
        collection_name=collection_name,
        client=chromadb.HttpClient(
            host=host_client, 
            port=port_client
        )
    )