import uuid
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_text_splitters.base import TextSplitter
from langchain.vectorstores import VectorStore

from src.logger import get_logger

LOGGER = get_logger()

class RAG:
    def __init__(self,
        name: str,
        type: str,
        embeddings: Embeddings, 
        chat_models: BaseChatModel, 
        vector_stores: VectorStore, 
        loader: BaseLoader, 
        text_splitter: TextSplitter
    ) -> None:
        self.name = name
        self.type = type
        self.embeddings = embeddings
        self.chat_models = chat_models
        self.vector_stores = vector_stores
        self.loader = loader
        self.text_splitter = text_splitter

    def index(self) -> None:
        docs = self.loader.load()
        chunks = self.text_splitter.split_documents(docs)
        uuids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        self.vector_store.add_documents(documents=chunks, ids=uuids)


    def query(self, query: str) -> str:
        ...