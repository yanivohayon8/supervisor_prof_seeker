
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


KEYWORD_TO_QUIT_CHATBOT = ["q", "exit", "quit"]

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
    
    def __init__(self,vector_store,user_input="keyboard"):
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


        self.user_input = user_input

        if isinstance(self.user_input,list):
            self.user_input_iterator_index = 0 

            assert all([isinstance(query,str) for query in self.user_input])
    
    def retrieve_(self,state:SimpleRAGState):
        retrieved_docs = self.vector_store.similarity_search(state["question"])
        return {"context":retrieved_docs}

    def generate_(self, state:SimpleRAGState):
        docs_content = "\n\n".join([docs.page_content for docs in state["context"]])
        prompt_value = self.prompt.invoke({"docs_content":docs_content,"question":state["question"]})
        response = self.llm.invoke(prompt_value)

        return {"answer":response.content}

    def run_mock_client(self,thread_id="aaa"):
        config = {"configurable":{"thread_id":thread_id}}

        while True:
            try:
                user_input = self.get_user_input()
                print(f"Recieved user input: {user_input}")
                if user_input in KEYWORD_TO_QUIT_CHATBOT:
                    print("Goodbye")
                    break
                
                for word in self.stream_answer(user_input,config):
                    print(word)

            except Exception as e:
                user_input = "What is Bob?"
                # self.stream_graph_update_mock_client_(user_input,config)
                for word in self.stream_answer(user_input,config):
                    print(word)
                print("Goodbye")
                break
    

    def get_user_input(self):
        if self.user_input == "keyboard":
            return input("User:")
                
        if isinstance(self.user_input,list):
            if self.user_input_iterator_index == len(self.user_input):
                return KEYWORD_TO_QUIT_CHATBOT[0]
            
            next_query = self.user_input[self.user_input_iterator_index]
            self.user_input_iterator_index +=1

            return next_query
        
    def get_config(self):
        thread_id = str(uuid.uuid4())
        return {"configurable":{"thread_id":thread_id}}

    def stream_answer(self,user_input:str,config):
        for chunk, metadata in self.graph.stream({"question":user_input},
                                                 config=config,stream_mode="messages"):
            if isinstance(chunk,AIMessage):
                yield chunk.content
