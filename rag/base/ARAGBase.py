from abc import ABC, abstractmethod

class ARAGBase(ABC):
    """
    Abstract base class for a RAG (Retrieval-Augmented Generation) system.
    """
    @abstractmethod
    def _build(self) -> None:
        """
        Build the RAG system.
        This method should be implemented to set up the necessary components
        such as loaders, embeddings, vector stores, etc.
        """
        pass

    @abstractmethod
    def index(self) -> str:
        """
        create indexes of documents for retrieval.
        """
        pass

    @abstractmethod
    def query(self, query: str) -> str:
        """
        Use the query to retrieve context.
        Then context + query + system prompt --> answer. 

        :param query: The input query string.
        :return: A list of relevant documents.
        """
        pass