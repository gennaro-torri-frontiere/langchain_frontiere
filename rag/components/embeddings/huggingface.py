from langchain.embeddings import HuggingFaceEmbeddings

def bge_small() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")