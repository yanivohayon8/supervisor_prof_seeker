import unittest
from src.api_utils import get_chat_langchain_openai_new,get_langchain_openai_lunary_

class TestLunaryWrapper(unittest.TestCase):

    def test_public_key(self):
        llm = get_langchain_openai_lunary_()

        response = llm.invoke("echo Success")
        self.assertIn("Success", response.content)


if __name__ == "__main__":
    unittest.main()