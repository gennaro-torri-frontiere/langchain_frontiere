import re
import uuid

def normalize_doc(doc):
    """
    Normalize the document by removing extra spaces, normalizing punctuation,
    and converting to lowercase.
    Input:
        doc: The document to be normalized.
    Output:
        doc: The normalized document.
    """
    s = doc.page_content
    # Remove extra spaces and normalize punctuation
    # Keep dates in the format dd/mm/yyyy
    s = re.sub(r'\s+', ' ', s).strip()  # Normalize spaces
    s = re.sub(r"(?<!\d)/|(?!\d)/", " ", s)  # Do not touch slashes in dates
    s = re.sub(r"\s*[^\w\s.,;!?'-]\s*", "", s)  # Remove non-alphanumeric characters (e.g., strange symbols)
    s = s.replace("..", ".").replace(". .", ".")  # Fix specific punctuation cases
    s = s.replace("\n", " ").strip()  # Remove line breaks
    doc.page_content = s.lower()  # Convert everything to lowercase for uniformity

    return doc

def index(document_loader, splitter, vector_store):
    """
    Index the documents into the vector store.

    Input:
        docs: The documents to be indexed.
        chunks: The chunks of documents.
        uuids: The unique identifiers for each chunk.
        vector_store: The vector store to index the documents into.
    Output:
        Vecotor store with indexed documents.
    """

    docs = document_loader.load()
    chunks = splitter.split_documents(map(normalize_doc, docs))
    uuids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    vector_store.add_documents(documents=chunks, ids=uuids)
    
    return vector_store

