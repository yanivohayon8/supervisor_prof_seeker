
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



class SimpleState(TypedDict):
    messages: Annotated[list, add_messages]

class SimpleChatbot:

    def __init__(self):
        verify_openai_api_key()
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")

        self.graph_builder = StateGraph(SimpleState)
        
        self.graph_builder.add_node("chatbot_",self.chatbot_)
        self.graph_builder.add_edge(START, "chatbot_")
        self.graph_builder.add_edge("chatbot_",END)

        self.graph = self.graph_builder.compile(checkpointer=MemorySaver())
    
    def chatbot_(self,state:SimpleState):
        return {"messages": [self.llm.invoke(state["messages"])]}

    def stream_graph_updates(self, query,config):
        for chunk,metadata in self.graph.stream({"messages":[{"role":"user","content":query}]},config,stream_mode="messages"):
            if isinstance(chunk,AIMessage):
                print(chunk.content, end="")
        
        print()
            # for val in event.values():
            #     print("Assistant:", val["messages"][-1].content)

    def run(self,thread_id="aaaa"):
        # thread_id = str(uuid.uuid4())
        # print(f"initiate a conversation with thread id {thread_id}")

        config = {"configurable":{"thread_id":thread_id}} # can support multi-tentants

        while True:
            try:
                user_input = input("User:")
                print("User: " + user_input)
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goddbye!")
                    break

                self.stream_graph_updates(user_input,config)
            except Exception as e:
                user_input = "exit"
                print("User: " + user_input)
                self.stream_graph_updates(user_input,config)
                break


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
            ("system", "You are an assistant for question-answering tasks. Use the following context to answer." +
                        " If you do not know the answer say you do not know. Answer concisely."
                        "\n\n {docs_content}"),
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
    
    def stream_graph_update(self, user_input,config):
        for step in self.graph.stream({"question":user_input},config=config):
            if "generate_" in step.keys():
                print(step["generate_"]["answer"])


    def run(self,thread_id="aaa"):
        config = {"configurable":{"thread_id":thread_id}}

        while True:
            try:
                user_input = input("User:")
                print()
                if user_input in ["q", "exit", "quit"]:
                    print("Goodbye")
                    break
                
                self.stream_graph_update(user_input,config)

            except Exception as e:
                user_input = "What is Bob?"
                self.stream_graph_update(user_input,config)
                print("Goodbye")
                break
