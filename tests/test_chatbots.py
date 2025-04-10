import unittest
from src.chatbots.simple import SimpleRAGChatbot
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from src.api_utils import verify_openai_api_key
from langchain_core.documents import Document
from src.vector_store_loaders.faiss_loader import load_faiss_indexed

class TestSimpleRAGChatbot(unittest.TestCase):
    def test_run_single_user(self):
        verify_openai_api_key()
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = InMemoryVectorStore(embeddings)

        docs = [
            Document(page_content="Bob is to strike with a quick light blow"),
            Document(page_content="Snark is an informal word that refers to an attitude or expression of mocking irreverence and sarcasm."),
            Document(page_content="Someone or something described as effusive is expressing or showing a lot of emotion or enthusiasm."),
            Document(page_content="Penchant refers to a strong liking for something, or a strong tendency to behave in a certain way. It is usually used with for."),
            # Document(page_content="Untoward is a formal word that describes something that is improper or inappropriate, or that is adverse or unfavorable."),
            Document(page_content="Yaniv is an AI expert.")
        ]
        vector_store.add_documents(docs)

        queries = ["I want to do a research on deep learning. Do you recommend on a supervisor?","Who is Bob?"]
        bot = SimpleRAGChatbot(vector_store)

        for ans in bot.run_mock_client(queries):
            self.assertIsInstance(ans,str)
            print(ans)
    
    def test_run_fixed_queries_1(self):
        vector_store = load_faiss_indexed()
        queries = ["I want to do a research on deep learning. Do you recommend on a supervisor?"]
        bot = SimpleRAGChatbot(vector_store)
        
        for ans in bot.run_mock_client(queries):
            self.assertIsInstance(ans,str)
            print(ans)

if __name__ == "__main__":
    unittest.main()