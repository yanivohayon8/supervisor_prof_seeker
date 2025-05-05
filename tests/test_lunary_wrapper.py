import unittest
from src.api_utils import get_langchain_openai_lunary_,verify_openai_api_key,get_chat_langchain_openai_new
from src.chatbots.lunary_wrapper import ConversationRecorder
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from src.chatbots.simple import SimpleRAGChatbot
from src.vector_store_loaders.faiss_loader import load_faiss_indexed


class TestLunaryAcessAPI(unittest.TestCase):
    def test_public_key(self):
        llm = get_langchain_openai_lunary_()

        response = llm.invoke("echo Success")
        self.assertIn("Success", response.content)

    
class TestLunaryWrapper(unittest.TestCase):
    unittest_tags =["compiling_unit_tests"]

    def test_track_only_users(self):
        thread_wrapper = ConversationRecorder(tags=self.unittest_tags)

        thread_wrapper.track_user("Hi there, I am a new user!")
        thread_wrapper.track_user("Hello, I am the same user")

        # View in the web application the last conversation for verfication

    def test_track_only_assistant(self):
        llm = get_langchain_openai_lunary_()
        thread_wrapper = ConversationRecorder(tags=self.unittest_tags)

        response = thread_wrapper.track_assistant(llm,"Say Welcome")
        self.assertIn("Welcome",response.content)

        # View in the web application the last conversation for verfication

    def test_track_user_assistant(self):
        llm = get_langchain_openai_lunary_()
        thread_wrapper = ConversationRecorder(tags=self.unittest_tags)

        user_inputs = ["Who are you?", "What is the result of 5 plus 5?"]

        for i,user_in in enumerate(user_inputs):
            thread_wrapper.track_user(user_in)
            thread_wrapper.track_assistant(llm,user_in)

            if i % 2 == 0:
                thread_wrapper.positive_feedback_last_message()
            elif i % 2 == 1:
                thread_wrapper.negative_feedback_last_message()

        # View in the web application the last conversation for verfication

    
    def test_simple_chat_bot_InMemoryVectorStore(self):
        verify_openai_api_key()
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = InMemoryVectorStore(embeddings)
        vector_store.add_documents(
            [
                Document(page_content="LangGraph is built for developers who want to build powerful, adaptable AI agents."),
                Document(page_content="Lunary is an open-source platform for developers of AI chatbots and other LLM-powered applications.")
            ]
        )

        llm = get_langchain_openai_lunary_()
        conversation_recorder = ConversationRecorder(tags=self.unittest_tags)
        bot = SimpleRAGChatbot(llm,vector_store,converstation_recorder=conversation_recorder)
        
        res = bot.invoke_answer("For who does LangGraph is built? Answer shortly")
        # A naive string matching here is enough just to see that the function above works
        self.assertIn("developers",res["answer"])

        res = bot.invoke_answer("What is Lunary? Answer shortly")
        self.assertIn("Lunary",res["answer"])
    
    def test_simple_chat_bot_faiss_db_invoke_answer(self):
        vector_store = load_faiss_indexed()
        llm = get_chat_langchain_openai_new(is_lunary_audit=True)
        conversation_recorder = ConversationRecorder(tags=self.unittest_tags)
        bot = SimpleRAGChatbot(llm,vector_store,converstation_recorder=conversation_recorder)
        
        user_inputs = [
            "I want to do cool things with AI, list some relevent supervisors?",
            "Do you know others?",
            "Who is specialized with Deep Learning?"
        ]

        for user_input in user_inputs:
            print()
            print("********************** User **************************")
            print(user_input)
            invoke_result = bot.invoke_answer(user_input)
            answer = invoke_result.get("answer")
            print("********************** answer **************************")
            print(answer)
    
    def test_simple_chat_bot_faiss_db_mock_streaming(self):
        vector_store = load_faiss_indexed()
        llm = get_chat_langchain_openai_new(is_lunary_audit=True)
        conversation_recorder = ConversationRecorder(tags=self.unittest_tags)
        bot = SimpleRAGChatbot(llm,vector_store,converstation_recorder=conversation_recorder)
        
        user_inputs = [
            "I want to do cool things with AI, list some relevent supervisors?",
            "Do you know others?",
            "Who is specialized with Deep Learning?"
        ]

        config = bot.get_config_deprecated()
        i = 0

        for answer in bot.mock_streaming(user_inputs,config=config):
            print()
            print("********************** User **************************")
            print(user_inputs[i])
            i+=1
            print("********************** answer **************************")
            print(answer)
            print()





if __name__ == "__main__":
    unittest.main()