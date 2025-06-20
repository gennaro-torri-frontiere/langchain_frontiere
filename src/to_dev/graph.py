from langchain_core.prompts import PromptTemplate
from langgraph.graph import START, StateGraph
from to_dev.state import State

class Graph():

    def __init__(self,vector_store, Model):
        """
        Initialize the Graph class with a vector store and a model.
        Input:
            vector_store: The vector store to search for relevant documents.
            Model: The model to generate answers.
        """
        
        self.template =(
        "You are a chatbot assistant specialized in construction site timelines. "
        "Your task is to answer questions about the chronology of work based strictly on the provided context. "
        "The context may contain text in different languages (English, Italian, Swedish). "
        "Your task is to answer questions about the chronology of work based strictly on the provided context. "
        "The context may contain text in different languages (English, Italian, Swedish). "
        "If the context is not in English, translate it in english before answering, but do not mention that a translation was performed. "
        "respond only in English. "
        "Dates may be written in different formats such as '12/11/2024', 'November 12, 2024', '12th November 2024', or '12 nov 2024'. "
        "Always match dates correctly regardless of the format. "
        "If a day was non-working, state that work was halted and provide the reason from the document. "
        "If work was carried out, describe exactly what was done on that day, without omitting details. "
        "Do not add any information that is not explicitly mentioned in the context. "
        "If the context does not contain relevant information, respond with: 'I do not have information on this'."
        "{context}"
        "Question: {question}"
        "Helpful Answer:"
        ) 
        self.custom_rag_prompt = PromptTemplate.from_template(self.template)
        self.graph = None
        self.llm = Model
        self.vector_store = vector_store

        
    def retrieve(self,state: State):
        """
        Retrieve relevant documents based on the question.
        Input:
            state: A dictionary containing the question.
            vector_store: The vector store to search for relevant documents.
        Output:
            A dictionary containing the retrieved documents.
        """
        retrieved_docs = self.vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}


    def generate(self, state: State):
        """
        Generate an answer based on the retrieved documents and the question.
        Input:
            state: A dictionary containing the question and context.
        Output:
            A dictionary containing the answer.
        """
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.custom_rag_prompt.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}
    
    def create_graph(self, list_function):
        """
        Create a state graph with the given retrieve and generate functions.
        Input:
            retrieve: Function to retrieve documents based on the question.
            generate: Function to generate an answer based on the retrieved documents.
        Output:
            A state graph object.
        """
       #graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder = StateGraph(State).add_sequence(list_function)
        graph_builder.add_edge(START, list_function[0])
        self.graph = graph_builder.compile()

    def chat(self, question:str):
        """
        chat with the user by invoking the graph with the question.
        Input:
            question: The user's question.
        Output:
            A dictionary containing the answer.
        """

        return self.graph.invoke({f"question": question})

     