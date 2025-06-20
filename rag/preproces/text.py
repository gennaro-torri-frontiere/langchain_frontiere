import re
from langchain_core.documents.base import Document

def clean(doc: Document) -> Document:
    """
    Normalizza il contenuto del documento rimuovendo spazi, caratteri extra e gestendo la punteggiatura.
    Le date nel formato dd/mm/yyyy rimangono inalterate.
    """
    s = doc.page_content
    
    # Rimuovi spazi extra e normalizza la punteggiatura
    # Mantieni le date in formato dd/mm/yyyy
    s = re.sub(r'\s+', ' ', s).strip()  # Normalizza gli spazi
    s = re.sub(r"(?<!\d)/|(?!\d)/", " ", s)  # Non tocca le barre nelle date
    s = re.sub(r"\s*[^\w\s.,;!?'-]\s*", "", s)  # Rimuove caratteri non alfanumerici (es. simboli strani)
    s = s.replace("..", ".").replace(". .", ".")  # Corregge casi particolari di punteggiatura
    s = s.replace("\n", " ").strip()  # Rimuove line break
    doc.page_content = s.lower()  # Converte tutto in minuscolo per uniformità
    return doc