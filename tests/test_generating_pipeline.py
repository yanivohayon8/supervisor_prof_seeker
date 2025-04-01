import unittest
from src.generating_pipeline.generating_pipeline import GeneratingPipeline

class TestGeneratingPipeline(unittest.TestCase):

    def test_loading_faiss(self):
        pipeline = GeneratingPipeline()

if __name__ == "__main__":
    unittest.main()