import yaml
import chromadb
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.utils import load_config


class Factory:
    def __init__(self):
        self.config = load_config('rag_config.yml')
        self.instances = {
            'language_model': {},
            'vector_store': {},
            'embedding': {},
            'retriever': {},
            'document_loader': {},
            'text_splitter': {}
        }

    def get_document_loader(self, rag_name: str) -> object:
        name = self.config[rag_name]['document_loader']['name']
        class_ = self.config[rag_name]['document_loader']['class']

        if name not in self.instances['document_loader']:
            if class_ == 'DirectoryLoader':
                self.instances['document_loader'][name] = DirectoryLoader(
                    **self.config[rag_name]['document_loader']['params']
                )
            else:
                raise ValueError(f"Document loader type {name} is not supported.")

        return self.instances['document_loader'][name]
    
    def get_text_splitter(self, rag_name: str) -> object:
        name = self.config[rag_name]['text_splitter']['name']
        class_ = self.config[rag_name]['text_splitter']['class']

        if name not in self.instances['text_splitter']:
            if class_ == 'RecursiveCharacterTextSplitter':
                self.instances['text_splitter'][name] = RecursiveCharacterTextSplitter(
                    **self.config[rag_name]['text_splitter']['params']
                )
            else:
                raise ValueError(f"Text splitter type {name} is not supported.")

        return self.instances['text_splitter'][name]

    def get_embedding(self, rag_name: str) -> object:
        name = self.config[rag_name]['embedding']['name']
        class_ = self.config[rag_name]['embedding']['class']

        if name not in self.instances['embedding'].keys():
            if class_ == 'HuggingFaceBgeEmbeddings':
                self.instances['embedding'][name] = HuggingFaceEmbeddings(
                    **self.config[rag_name]['embedding']['params']
                )
            else:
                raise ValueError(f"Language model type {class_} is not supported.")

        return self.instances['embedding'][name]

    def get_vector_store(self, rag_name: str) -> object:
        name = self.config[rag_name]['vector_store']['name']
        class_ = self.config[rag_name]['vector_store']['class']
            
        if name not in self.instances['vector_store']:
            if class_ == 'Chroma':
                self.instances['vector_store'][name] = Chroma(
                    embedding_function=self.get_embedding(rag_name),
                    collection_name=self.config[rag_name]['vector_store']['collection_name'],
                    client=chromadb.HttpClient(
                        host=self.config[rag_name]['vector_store']['client']['host'], 
                        port=self.config[rag_name]['vector_store']['client']['port']
                    )
                )
            else:
                raise ValueError(f"Vector store type {name} is not supported.")

        return self.instances['vector_store'][name]

    def get_retriever(self, rag_name: str) -> object:
        name = self.config[rag_name]['retriever']['name']
        class_ = self.config[rag_name]['retriever']['class']

        if name not in self.instances['retriever']:
            if class_ == 'Chroma':
                vector_store = self.get_vector_store(rag_name)
                self.instances['retriever'][name] = vector_store.as_retriever(
                    **self.config[rag_name]['retriever']['params']
                )
            else:
                raise ValueError(f"Retriever type {name} is not supported.")

        return self.instances['retriever'][name]
    
    def get_language_model(self, rag_name: str) -> object:
        name = self.config[rag_name]['language_model']['name']
        class_ = self.config[rag_name]['language_model']['class']

        if name not in self.instances['language_model'].keys():
            if class_ == 'ChatOpenAI':
                self.instances['language_model'][name] = ChatOpenAI(
                    **self.config[rag_name]['language_model']['params']
                )
            else:
                raise ValueError(f"Language model type {class_} is not supported.")

        return self.instances['language_model'][name]
    