import inspect
import chromadb
from langchain_core.embeddings import Embeddings
from langchain.vectorstores import Chroma



def chroma_client(
        collection_name: str, 
        host_client: str, 
        port_client: str, 
        embedding_function: Embeddings) -> Chroma:
    """
    class: Chroma
    istanziata con un client HTTP per ChromaDB e una funzione di embedding specificata.
    """
    return Chroma(
        embedding_function=embedding_function,
        collection_name=collection_name,
        client=chromadb.HttpClient(
            host=host_client, 
            port=port_client
        )
    )