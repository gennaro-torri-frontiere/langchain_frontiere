# %%
%load_ext autoreload
%autoreload 2

# %%
import sys
import os
os.chdir('/app')
sys.path.append('/app')

# %%
from factory import Factory

# %%
fact = Factory()

# %%
# fact.config

# %%
document_loader = fact.get_document_loader('simple_rag')
splitter = fact.get_text_splitter('simple_rag')
vector_store = fact.get_vector_store('simple_rag')
retriever = fact.get_retriever('simple_rag')
llm = fact.get_language_model('simple_rag')

# %%
import re

def normalize_doc(doc):
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

# %%
document_loader, vector_store, retriever, llm, splitter

# %% [markdown]
# ### logica indexer

# %%
import uuid
docs = document_loader.load()
chunks = splitter.split_documents(map(normalize_doc, docs))
uuids = [str(uuid.uuid4()) for _ in range(len(chunks))]
vector_store.add_documents(documents=chunks, ids=uuids)

# %%
vector_store.similarity_search_with_score(
    'Controllo e livellamento del cemento dopo il getto'
)

# %% [markdown]
# ### Chatbot

# %%
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda




# %%
RunnablePassthrough().invoke('aaaaaaaaaaaaa')

# %%
system_prompt = (
    "You are a chatbot assistant specialized in construction site timelines. "
    "Your task is to answer questions about the chronology of work based strictly on the provided context. "
    "The context may contain text in different languages (English, Italian, Swedish). "
    "If the context is not in English, translate it before answering, but do not mention that a translation was performed. "
    "Dates may be written in different formats such as '12/11/2024', 'November 12, 2024', '12th November 2024', or '12 nov 2024'. "
    "Always match dates correctly regardless of the format. "
    "If a day was non-working, state that work was halted and provide the reason from the document. "
    "If work was carried out, describe exactly what was done on that day, without omitting details. "
    "Do not add any information that is not explicitly mentioned in the context. "
    "If the context does not contain relevant information, respond with: 'I do not have information on this'."
    "\nContext: {context}\nQuestion: {input}\nAnswer:"
)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(
    self.model, qa_prompt)

contextualize_q_system_prompt = (
    "Data una cronologia della chat e l'ultima domanda dell'utente,"
    "che potrebbe fare riferimento al contesto nella cronologia della chat, "
    "formulare una domanda autonoma che possa essere compresa "
    "senza la cronologia della chat. NON rispondere alla domanda, "
    "riformularla se necessario e altrimenti restituirla così com'è."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    self.model, self.retriever, contextualize_q_prompt)

rag_chain = create_retrieval_chain(
    history_aware_retriever, question_answer_chain)

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    self.get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

return conversational_rag_chain

# %%
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

# Definizione del prompt
retrieval_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an assistant that answers questions based on the provided context."),
        ("human", "{input}"),
    ]
)

# Creazione della retrieval chain
retrieval_chain = create_retrieval_chain(retriever, llm, retrieval_prompt)

# Esecuzione della chain con una domanda
response = retrieval_chain.invoke({"input": "Quali sono i dettagli del progetto del 15/01/2025?"})
print(response)

# %%


chats_store = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in chats_store:
        chats_store[session_id] = ChatMessageHistory()
    return chats_store[session_id]


system_prompt = (
    "You are a chatbot assistant specialized in construction site timelines. "
    "Your task is to answer questions about the chronology of work based strictly on the provided context. "
    "The context may contain text in different languages (English, Italian, Swedish). "
    "If the context is not in English, translate it before answering, but do not mention that a translation was performed. "
    "Dates may be written in different formats such as '12/11/2024', 'November 12, 2024', '12th November 2024', or '12 nov 2024'. "
    "Always match dates correctly regardless of the format. "
    "If a day was non-working, state that work was halted and provide the reason from the document. "
    "If work was carried out, describe exactly what was done on that day, without omitting details. "
    "Do not add any information that is not explicitly mentioned in the context. "
    "If the context does not contain relevant information, respond with: 'I do not have information on this'."
    "Context: {context}:"
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
    ]
)

# {"context": retriever | StrOutputParser(), "question": RunnablePassthrough()} 

chain = create_history_aware_retriever(retriever, llm, prompt)


history_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
    # output_messages_key="answer",
)

session_id = str(uuid.uuid4())
question = "Cosa è successo il 15/01/2025?"

result = history_chain.invoke(
    {"input": question},
    config={
        "configurable": {"session_id": session_id}
    }
)
# result = chain.invoke(question)


# %%
result

# %%
prompt = PromptTemplate.from_template("Say {foo}")
rag = prompt | llm

# %%
rag.invoke({'foo': 'hello in french'})

# %%
retriever.invoke('Controllo e livellamento del cemento dopo il getto')


