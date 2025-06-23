import uuid
from typing import Callable, Tuple
from importlib import import_module
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_text_splitters.base import TextSplitter
from langchain.vectorstores import VectorStore
from langchain_core.vectorstores import VectorStoreRetriever

import rag.components.chat_models as chat_models
import rag.components.loader as loader
import rag.components.splitter as splitter
import rag.components.vectore_store as vectore_store
from rag.base.ARAGBase import ARAGBase
from src.logger import get_logger
from src.utils import load_config, call_function

LOGGER = get_logger()

class RAGBase(ARAGBase):

    def __init__(self, name: str, config_path: dict) -> None:
        self.logger = get_logger()
        self.name = name
        self.config_template: dict = load_config('rag/base/config/config_template.yml')
        self.config: dict = load_config(config_path)
        self._check_config()
        self._build()

    def _check_config(self) -> None:
        components: dict = self.config.get('components', {})
        required_components = {"embeddings", "chat_models", "vectore_store", "loader", "splitter"}

        assert set(components.keys()) == required_components, \
            f"Config must contain exactly one component of each type: {required_components}"
        assert len(components.keys()) == 5, \
            f"Config must contain exactly one component of each type: {required_components}"
        assert self.config.get('retriever_params', {}), "Config must contain 'retriever_params'" 
        assert self.config.get('system_prompt_file', {}), "Config must contain 'system_prompt_file'"

    def _read_info(self, component: str) -> Tuple[str, str, dict]:
        '''
        from a dict like 
        {
            "name": "chroma_client",
            "module_path": "rag.components.vectore_store.chroma",
            "params": {}
        }
        return name, module_path, params
        '''
        return self.config['components'][component]['name'],\
               self.config['components'][component]['module_path'],\
               self.config['components'][component]['params']

    def _build(self) -> None:
        # Chat Models
        function_name, module_path, params = self._read_info('chat_models')
        self.logger.info(f"Creating component {function_name} with params {params}")
        self.chat_models: BaseChatModel = call_function(
            module=module_path,
            func=function_name,
            **params
        )

        # Embeddings
        function_name, module_path, params = self._read_info('embeddings')
        self.logger.info(f"Creating component Embeddings with {function_name}")
        self.embedding: Embeddings = call_function(
            module=module_path,
            func=function_name,
            **params
        )

        # Vector Stores
        function_name, module_path, params = self._read_info('vectore_store')
        self.logger.info(f"Creating component Vector Stores with {function_name}")
        self.vector_stores: VectorStore = call_function(
            module=module_path,
            func=function_name,
            embedding_function=self.embedding,
            **params
        )
        self.logger.info(f"creating retriever from vectore store")
        self.retriever: VectorStoreRetriever = self.vector_stores.as_retriever(**self.config['retriever_params'])

        # Loader
        function_name, module_path, params = self._read_info('loader')
        self.logger.info(f"Creating component Loader with {function_name}")
        self.loader: BaseLoader = call_function(
            module=module_path,
            func=function_name,
            **params
        )

        # Text Splitter
        function_name, module_path, params = self._read_info('splitter')
        self.logger.info(f"Creating component Splitter with {function_name}")
        self.splitter: TextSplitter = call_function(
            module=module_path,
            func=function_name,
            **params
        )

        if self.config["preproces"]:
            function_name = self.config["preproces"]["name"]
            module_path = self.config["preproces"]["module_path"]
            self.logger.info(f"preproces config: {self.config['preproces']}")
            self.preproces_func = getattr(import_module(module_path), function_name)
            self.preproces_parmas = self.config["preproces"]["params"] or {}
        else:
            self.preproces_func = None
            self.preproces_parmas = None

        with open(self.config['system_prompt_file'], 'r') as f:
            self.system_prompt: str = f.read()

        self.logger.info('build completed successfully.')

    def index(self) -> None:
        docs = self.loader.load()
        if self.preproces_func:
            docs = list(map(self.preproces_func, docs))
        chunks = self.splitter.split_documents(docs)
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