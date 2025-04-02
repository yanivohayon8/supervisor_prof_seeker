
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from src.api_utils import verify_openai_api_key
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
import uuid
from langchain_core.messages import AIMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]

class SimpleChatbot:

    def __init__(self):
        verify_openai_api_key()
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")

        self.graph_builder = StateGraph(State)
        
        self.graph_builder.add_node("chatbot_",self.chatbot_)
        self.graph_builder.add_edge(START, "chatbot_")
        self.graph_builder.add_edge("chatbot_",END)

        self.graph = self.graph_builder.compile(checkpointer=MemorySaver())
    
    def chatbot_(self,state:State):
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