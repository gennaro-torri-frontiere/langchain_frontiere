from langchain_community.document_loaders import DirectoryLoader

def document_loader(path) -> DirectoryLoader:
    return DirectoryLoader(path=path)   
