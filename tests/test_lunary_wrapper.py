import unittest
from src.api_utils import get_langchain_openai_lunary_
from src.chatbots.lunary_wrapper import ThreadWrapper

class TestLunaryAcessAPI(unittest.TestCase):
    def test_public_key(self):
        llm = get_langchain_openai_lunary_()

        response = llm.invoke("echo Success")
        self.assertIn("Success", response.content)

    
class TestLunaryWrapper(unittest.TestCase):
    unittest_tags =["compiling_unit_tests"]

    def test_track_users(self):
        thread_wrapper = ThreadWrapper(tags=self.unittest_tags)

        thread_wrapper.track_user("Hi there, I am a new user!")
        thread_wrapper.track_user("Hello, I am the same user")

        # View in the web application the last conversation for verfication



if __name__ == "__main__":
    unittest.main()