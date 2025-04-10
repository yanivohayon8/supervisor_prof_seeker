
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from src.api_utils import verify_openai_api_key
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
import uuid
from langchain_core.messages import AIMessage
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate



KEYWORD_TO_QUIT_CHATBOT = ["q", "exit", "quit"]

class SimpleRAGState(TypedDict):
    question:str
    context:list[Document]
    answer:str

class SimpleRAGChatbot():
    
    def __init__(self,vector_store):
        verify_openai_api_key()
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        self.vector_store = vector_store

        self.graph_builder = StateGraph(SimpleRAGState)
        self.graph_builder.add_node("retrieve_",self.retrieve_)
        self.graph_builder.add_node("generate_",self.generate_)
        self.graph_builder.add_edge(START,"retrieve_")
        self.graph_builder.add_edge("retrieve_","generate_")
        self.graph_builder.add_edge("generate_",END)

        self.graph = self.graph_builder.compile(checkpointer=MemorySaver())
        self.prompt = ChatPromptTemplate([
            ("system", 
                "You are an expert assistant designed to help M.Sc. and Ph.D. students find a suitable research supervisor. "
                "Use the provided context to answer questions accurately and concisely. "
                "If the answer is not in the given context, say you do not know instead of making assumptions."
                "\n\nContext:\n{docs_content}"
            ),
            ("human", "Question: {question}")
        ])

    
    def retrieve_(self,state:SimpleRAGState):
        retrieved_docs = self.vector_store.similarity_search(state["question"])
        return {"context":retrieved_docs}

    def generate_(self, state:SimpleRAGState):
        docs_content = "\n\n".join([docs.page_content for docs in state["context"]])
        prompt_value = self.prompt.invoke({"docs_content":docs_content,"question":state["question"]})
        response = self.llm.invoke(prompt_value)

        return {"answer":response.content}

    def run_mock_client(self,queries:list[str],thread_id="aaa"):
        config = {"configurable":{"thread_id":thread_id}}
        
        for query in queries:
            query_response = ""
            for token in self.stream_answer(query,config):
                query_response += token
            
            yield query_response
        
    def get_config(self):
        thread_id = str(uuid.uuid4())
        return {"configurable":{"thread_id":thread_id}}

    def stream_answer(self,user_input:str,config):
        for chunk, metadata in self.graph.stream({"question":user_input},
                                                 config=config,stream_mode="messages"):
            if isinstance(chunk,AIMessage):
                yield chunk.content
