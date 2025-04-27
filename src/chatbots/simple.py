
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver
import uuid
from langchain_core.messages import AIMessage
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.vectorstores import VectorStore
from typing import TypedDict, List, Optional

KEYWORD_TO_QUIT_CHATBOT = ["q", "exit", "quit"]

class SimpleRAGState(TypedDict):
    question: str
    context: List[Document]
    answer: str
    chat_history: List[tuple[str, str]]  # <-- NEW: history of (question, answer) pairs

class SimpleRAGChatbot():

    def __init__(self, llm: BaseLanguageModel, vector_store: VectorStore, prompt: Optional[ChatPromptTemplate] = None, max_turns: int = 5):
        self.llm = llm
        self.vector_store = vector_store
        self.max_turns = max_turns

        self.graph_builder = StateGraph(SimpleRAGState)
        self.graph_builder.add_node("retrieve_", self.retrieve_)
        self.graph_builder.add_node("generate_", self.generate_)
        self.graph_builder.add_edge(START, "retrieve_")
        self.graph_builder.add_edge("retrieve_", "generate_")
        self.graph_builder.add_edge("generate_", END)

        self.graph = self.graph_builder.compile(checkpointer=MemorySaver())

        if not prompt:
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", 
                    "You are an expert assistant designed to help M.Sc. and Ph.D. students find a suitable research supervisor. "
                    "Use the provided context to answer questions accurately and concisely. "
                    "\n\nContext:\n{docs_content}"
                ),
                ("human", "Previous conversation:\n{chat_history}\n\nNew Question: {question}")
            ])
        else:
            self.prompt = prompt

    def retrieve_(self, state: SimpleRAGState):
        retrieved_docs = self.vector_store.similarity_search(state["question"], k=20)
        # Pass along previous chat history
        return {
            "context": retrieved_docs,
            "chat_history": state.get("chat_history", [])
        }

    def generate_(self, state: SimpleRAGState):
        docs_content = "\n\n".join([doc.page_content for doc in state["context"]])

        previous_history = state.get("chat_history", [])
        trimmed_history = previous_history[-self.max_turns:]

        formatted_history = "\n".join([f"Q: {q}\nA: {a}" for q, a in trimmed_history])

        prompt_value = self.prompt.invoke({
            "docs_content": docs_content,
            "chat_history": formatted_history,
            "question": state["question"]
        })

        try:
            response = self.llm.invoke(prompt_value)
            answer = response.content
        except Exception as e:
            if "context length" in str(e).lower():
                # Handle token overflow specifically
                answer = (
                    "⚠️ Sorry, your conversation or documents became too long for the model to handle.\n"
                    "Please try asking a shorter question or clear some history."
                )
            else:
                # General error fallback
                answer = (
                    "⚠️ Sorry, an unexpected error occurred while generating a response."
                )

        updated_chat_history = trimmed_history + [(state["question"], answer)]

        return {
            "answer": answer,
            "chat_history": updated_chat_history
        }
    
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

    def invoke_answer(self, user_input:str,config:dict=None,**kwargs):
        if not config:
            config = self.get_config()

        return self.graph.invoke({"question":user_input},config=config,**kwargs)
