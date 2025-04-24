import unittest
from src.chatbots.simple import SimpleRAGChatbot
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from src.api_utils import verify_openai_api_key,get_llm_openai
from langchain_core.documents import Document
from src.vector_store_loaders.faiss_loader import load_faiss_indexed
from src.chatbots import openevals_wrapper
from src.indexing_pipeline.indexing_pipeline import get_supervisor_brief
from src.utils import load_chatbot_settings

class TestChatbotFunctions(unittest.TestCase):

    def test_invoke_answer(self):
        verify_openai_api_key()
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = InMemoryVectorStore(embeddings)
        vector_store.add_documents(
            [
                Document(page_content="LangGraph is built for developers who want to build powerful, adaptable AI agents.")
            ]
        )

        llm = get_llm_openai("gpt-4o-mini")
        bot = SimpleRAGChatbot(llm,vector_store)
        res = bot.invoke_answer("For who does LangGraph is built?")
        
        # A naive string matching here is enough just to see that the function above works
        self.assertIn("developers",res["answer"])


class TestStringMatching(unittest.TestCase):
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

        llm = get_llm_openai("gpt-4o-mini")
        bot = SimpleRAGChatbot(llm,vector_store)

        queries = ["Who is Bob?","I want to do a research on deep learning. Can you recommend on a supervisor?", "What was my first question?"]

        for ans in bot.run_mock_client(queries):
            self.assertIsInstance(ans,str)
            print(ans)
    
    def test_run_fixed_queries_1(self):
        vector_store = load_faiss_indexed()
        llm = get_llm_openai("gpt-4o-mini")
        bot = SimpleRAGChatbot(llm,vector_store)

        queries = ["I want to do a research on deep learning. Do you recommend on a supervisor?"]
        
        for ans in bot.run_mock_client(queries):
            self.assertIsInstance(ans,str)
            print(ans)


class TestLLMasJudge(unittest.TestCase):

    def build_bot_(self,model_name):
        vector_store = load_faiss_indexed()
        llm = get_llm_openai(model_name)
        bot = SimpleRAGChatbot(llm,vector_store)

        return bot 

    def test_supervisor_brief_1(self):
        settings = load_chatbot_settings()
        model_name = settings.get("model_name")
        bot = self.build_bot_(model_name)    

        supervisor_name = "Ohad-Ben Shahar"
        user_input = f"Who is {supervisor_name}?"
        res = bot.invoke_answer(user_input)
        answer = res["answer"]
        reference_outputs = get_supervisor_brief(supervisor_name,"Ben-Gurion University",["Computer Science", "Computer Vision"])

        judge_model = f"openai:{model_name}"

        correctness_result = openevals_wrapper.evaluate_correctness(judge_model,user_input,answer,reference_outputs=reference_outputs)
        self.assertTrue(correctness_result["score"])

        rag_helpfulness_result = openevals_wrapper.evaluate_rag_helpfulness(judge_model,user_input,answer)
        self.assertTrue(rag_helpfulness_result["score"])

    def test_list_supervisors_ai(self):
        settings = load_chatbot_settings()
        model_name = settings.get("model_name")
        bot = self.build_bot_(model_name)

        user_input = "I want to do a research on deep learning. Do you recommend on a supervisor?"
        invoke_result = bot.invoke_answer(user_input)

        judge_model = f"openai:{model_name}"
        
        answer = invoke_result.get("answer")
        context = invoke_result.get("context")

        rag_helpfulness_result = openevals_wrapper.evaluate_rag_helpfulness(judge_model,user_input,answer)
        self.assertTrue(rag_helpfulness_result["score"])

        rag_retrieval_relevance_result = openevals_wrapper.evaluate_rag_retrieval_relevance(judge_model,user_input,context)
        self.assertTrue(rag_retrieval_relevance_result["score"])

        rag_groundeness_result = openevals_wrapper.evaluate_rag_groundeness(judge_model,context,answer)
        self.assertTrue(rag_groundeness_result["score"])

        reference_outputs = "The following is a partial list of the supervisors of AI: Jihad El sana, Oren Freifeld, Gera Weiss, Sivan Sabato, and Omri Azencot"
        correctness_result = openevals_wrapper.evaluate_correctness(judge_model,user_input,answer,reference_outputs=reference_outputs)
        self.assertTrue(correctness_result["score"])


    
    






if __name__ == "__main__":
    unittest.main()