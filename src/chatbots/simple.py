
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
import re
from openai import BadRequestError
from src.chatbots.lunary_wrapper import ConversationRecorder

class SimpleRAGState(TypedDict):
    question: str
    context: List[Document]
    answer: str
    chat_history: List[tuple[str, str]]  # (question, answer) pairs

class SimpleRAGChatbot():

    def __init__(self, llm: BaseLanguageModel, vector_store: VectorStore,
                  graph_config:dict=None,converstation_recorder:ConversationRecorder=None, max_turns: int = 5):
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

        self.converstation_recorder = converstation_recorder

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
                "You are an expert assistant designed to help M.Sc. and Ph.D. students find a suitable research supervisor. "
                "Use the provided context to answer questions accurately and concisely. "
                "\n\nContext:\n{docs_content}"
            ),
            ("human", "Previous conversation:\n{chat_history}\n\nNew Question: {question}")
            ])

        # NOTE: Make sure you usually don't set graph_config to null (it is valid only for a single run in the tests, rather than using with streamlit)
        if not graph_config:
            graph_config = generate_graph_config()

        self.graph_config = graph_config

    def retrieve_(self, state: SimpleRAGState):
        retrieved_docs = self.vector_store.similarity_search(state["question"], k=20)
        
        return {
            "context": retrieved_docs,
            "chat_history": state.get("chat_history", [])
        }

    def generate_(self, state: SimpleRAGState):
        docs_content = "\n\n".join([doc.page_content for doc in state["context"]])

        previous_history = state.get("chat_history", [])
        trimmed_history = previous_history[-self.max_turns:]

        formatted_history = "\n".join([f"Q: {q}\nA: {a}" for q, a in trimmed_history])

        try:
            question = self.satnitize_question_(state["question"])
        except ValueError as e:
            answer = "Sorry, an unexpected error occurred while generating a response."
            # self.llm.invoke(f"Echo the following:{answer}") # To make it appear in the streamlit GUI (look at self.stream_answer function)
            self.echo_llm_catching_err_(answer)

            return {
                "answer": answer,
                "chat_history":trimmed_history
            }

        prompt_value = self.prompt.invoke({
            "docs_content": docs_content,
            "chat_history": formatted_history,
            "question": question
        })

        try:
            # response = self.llm.invoke(prompt_value)
            response = self.invoke_llm_(prompt_value)
            answer = response.content
        except BadRequestError as bre:
            if "context length" in str(bre).lower():
                # Handle token overflow specifically
                answer = "Sorry, your conversation or documents became too long for the model to handle.\n Please try asking a shorter question or clear some history."
                
            else:
                answer = "Sorry, an unexpected error occurred while generating a response."
            
            # self.llm.invoke(f"Echo the following:{answer}") # To make it appear in the streamlit GUI (look at self.stream_answer function)
            self.echo_llm_catching_err_(answer)

        updated_chat_history = trimmed_history + [(state["question"], answer)]

        return {
            "answer": answer,
            "chat_history": updated_chat_history
        }
    
    def satnitize_question_(self,question:str)->str:
        dangerous_phrases = [
            r"(?i)\bforget\b",
            r"(?i)\bignore\b",
            r"(?i)\byou are now\b",
            r"(?i)\bdisregard\b",
            r"(?i)\bpretend\b",
            r"(?i)\bassume\b"
        ]
        for pattern in dangerous_phrases:
            if re.search(pattern, question):
                raise ValueError("⚠️ Injection attempt detected. Please rephrase your question.")
        return question

    def stream_answer(self,user_input:str):
        self.track_user_(user_input)

        for chunk, metadata in self.graph.stream({"question":user_input},
                                                 config=self.graph_config,stream_mode="messages"):
            if isinstance(chunk,AIMessage):
                yield chunk.content

    def mock_streaming(self,queries:list[str]):
        for query in queries:
            query_response = ""
            for token in self.stream_answer(query):
                query_response += token
            
            yield query_response

    def graph_invoke(self, user_input:str,**kwargs):
        '''
            This function is ment for debugging
        '''
        # self.track_user_(user_input)
        
        return self.graph.invoke({"question":user_input},config=self.graph_config,**kwargs)


    def echo_llm_catching_err_(self,answer:str,invoke_params:dict={}):
        # To make the message about catching the error appear in the streamlit GUI (look at self.stream_answer function),
        # an invokation to the llm should occur. Therefore, to pass the message, echoing the catching error message to the user
        return self.invoke_llm_(f"Echo the following:{answer}",invoke_params=invoke_params)

    def invoke_llm_(self,user_input:str,invoke_params:dict={}):
        if not self.converstation_recorder:
            return self.llm.invoke(user_input,**invoke_params)
        else:
            return self.converstation_recorder.track_assistant(self.llm,user_input,**invoke_params,)

    def track_user_(self,user_input:str):
        if self.converstation_recorder:
            self.converstation_recorder.track_user(user_input)
   
    def track_positive_feedback(self,msg_index:int):
        self.converstation_recorder.positive_feedback(msg_index)
    
    def track_negative_feedback(self,msg_index:int):
        self.converstation_recorder.negative_feedback(msg_index)
    
    def track_delete_feedback(self,msg_index:int):
        self.converstation_recorder.delete_feedback(msg_index)


def generate_graph_config():
    thread_id = str(uuid.uuid4())
    return {"configurable":{"thread_id":thread_id}}
