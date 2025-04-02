import unittest
from src.chatbots.simple import SimpleChatbot


class TestSimple(unittest.TestCase):

    def test_run_single_user(self):
        bot = SimpleChatbot()
        bot.run()

if __name__ == "__main__":
    unittest.main()