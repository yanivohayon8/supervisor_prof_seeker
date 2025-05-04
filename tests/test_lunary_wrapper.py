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

    def test_track_only_users(self):
        thread_wrapper = ThreadWrapper(tags=self.unittest_tags)

        thread_wrapper.track_user("Hi there, I am a new user!")
        thread_wrapper.track_user("Hello, I am the same user")

        # View in the web application the last conversation for verfication

    def test_track_only_assistant(self):
        llm = get_langchain_openai_lunary_()
        thread_wrapper = ThreadWrapper(tags=self.unittest_tags)

        response = thread_wrapper.track_assistant(llm,"Say Welcome")
        self.assertIn("Welcome",response.content)

        # View in the web application the last conversation for verfication

    def test_track_user_assistant(self):
        llm = get_langchain_openai_lunary_()
        thread_wrapper = ThreadWrapper(tags=self.unittest_tags)

        user_inputs = ["Who are you?", "What is the result of 5 plus 5?"]

        for i,user_in in enumerate(user_inputs):
            thread_wrapper.track_user(user_in)
            thread_wrapper.track_assistant(llm,user_in)

            if i % 2 == 0:
                thread_wrapper.positive_feedback_last_message()
            elif i % 2 == 1:
                thread_wrapper.negative_feedback_last_message()

        # View in the web application the last conversation for verfication


if __name__ == "__main__":
    unittest.main()