import uuid
from typing import Callable
from importlib import import_module
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_text_splitters.base import TextSplitter
from langchain.vectorstores import VectorStore
from langchain_core.vectorstores import VectorStoreRetriever

import rag.components.chat_models as chat_models
import rag.components.loader as loader
import rag.components.text_splitter as text_splitter
import rag.components.vectore_store as vectore_store
from rag.base.ARAGBase import ARAGBase
from src.logger import get_logger
from src.utils import load_config

LOGGER = get_logger()

class RAGBase(ARAGBase):

    def __init__(self, name: str, config: dict) -> None:
        self.logger = get_logger()
        self.name = name
        self.config_blank: dict = load_config('rag/base/config/config_blank.yml')
        self._check_config(config)
        self._build(config)

    def _check_config(self, config) -> None:
        """
        check matching with config_blank
        """
        missing_keys = set(self.config_blank.keys()) - set(config.keys())
        if missing_keys:
            raise ValueError(f"Missing keys in config: {missing_keys}")
        extra_keys = set(config.keys()) - set(self.config_blank.keys())
        if extra_keys:
            raise ValueError(f"Extra keys in config: {extra_keys}")
        
        components = config.get("components", {})
        for component_name, component_config in components.items():
            if not isinstance(component_config, dict):
                raise ValueError(f"Component '{component_name}' must be a dictionary.")
            invalid_keys = set(component_config.keys()) - {"name", "params"}
            if invalid_keys:
                raise ValueError(
                    f"Component '{component_name}' has invalid keys: {invalid_keys}. "
                    "Only 'name' and 'params' are allowed."
                )
            
    def _build(self, config: dict) -> None:
        # Chat Models
        chat_models_name_func: str = config['components']['chat_models']['name']
        chat_models_func: Callable = getattr(chat_models, chat_models_name_func)
        chat_models_params: dict = config['components']['chat_models'].get("params", {}) or {}
        self.logger.info(f"chat_models components: {chat_models_name_func}")
        self.chat_models: BaseChatModel = chat_models_func(**chat_models_params)

        # Embeddings (used in vectore_store)
        embeddings_name_func: str = config['components']['embeddings']['name']
        embeddings_params: dict = config['components']['embeddings'].get("params", {}) or {}

        # Vector Stores
        vector_store_name_func: str = config['components']['vectore_store']['name']
        vector_store_func: Callable = getattr(vectore_store, vector_store_name_func)
        vector_store_params: dict = config['components']['vectore_store'].get("params", {}) or {}
        self.logger.info(f"vectore_store components: {vector_store_name_func} with {embeddings_name_func} embeddings")
        self.logger.info(f"vectore_store params: {vector_store_params}")
        self.vector_stores: VectorStore = vector_store_func(
            embeddings_name=embeddings_name_func,
            embeddings_params=embeddings_params,
            **vector_store_params
        )
        retriever_params: dict = config['retriever_params'].get("retriever_params", {}) or {}
        self.retriever: VectorStoreRetriever = self.vector_stores.as_retriever(**retriever_params)

        # Loader
        loader_name_func: str = config['components']['loader']['name']
        loader_func: Callable = getattr(loader, loader_name_func)
        loader_params: dict = config['components']['loader'].get("params", {}) or {}
        self.logger.info(f"loader components: {loader_name_func}")
        self.logger.info(f"loader params: {loader_params}")
        self.loader: BaseLoader = loader_func(**loader_params)

        # Text Splitter
        text_splitter_name_func: str = config['components']['text_splitter']['name']
        text_splitter_func: Callable = getattr(text_splitter, text_splitter_name_func)
        text_splitter_params: dict = config['components']['text_splitter'].get("params", {}) or {}
        self.logger.info(f"text_splitter components: {text_splitter_name_func}")
        self.logger.info(f"text_splitter params: {text_splitter_params}")
        self.text_splitter: TextSplitter = text_splitter_func(**text_splitter_params)

        if config["preproces"]:
            self.logger.info(f"preproces config: {config['preproces']}")
            type_: str = next(iter(config["preproces"].keys())) #eg. text
            self.logger.info(f"preproces type: {type_}")
            func_name: str = config["preproces"][type_]["name"]
            self.preproces_func: Callable = getattr(
                import_module(f'rag.preproces.{type_}'),
                func_name
            )
            self.preproces_parmas: dict = config["preproces"][type_].get("parmas", {}) or {}
        else:
            self.preproces_func = None
            self.preproces_parmas = None

        with open(config['system_prompt_file'], 'r') as f:
            self.system_prompt: str = f.read()

        self.logger.info('build completed successfully.')

    def index(self) -> None:
        docs = self.loader.load()
        if self.preproces_func:
            docs = list(map(self.preproces_func, docs))
        chunks = self.text_splitter.split_documents(docs)
        uuids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        self.vector_stores.add_documents(documents=chunks, ids=uuids)
        self.logger.info(
            f"RAG {self.name} indexed successfully."
            f"Stored {len(docs)} Documents with {len(chunks)} Chunks stored."
        )

    def query(self, query: str) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("system", "this is your context {context}"),
                ("user", "{input}")
            ]
        )
        document_chain  = create_stuff_documents_chain(
            llm=self.chat_models,
            prompt=prompt
        )
        retrieval_chain  = create_retrieval_chain(
            retriever=self.retriever,
            combine_docs_chain=document_chain
        )

        return retrieval_chain.invoke({"input": query})