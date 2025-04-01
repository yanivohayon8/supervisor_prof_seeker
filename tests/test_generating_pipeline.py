import unittest
from src.generating_pipeline.generating_pipeline import GeneratingPipeline

class TestGeneratingPipeline(unittest.TestCase):

    def test_loading_faiss(self):
        pipeline = GeneratingPipeline()

        query = "Ancient artworks are obtained in archaeological excavations."
        similar_docs = pipeline.similarity_search(query,k=1)

        self.assertEqual(len(similar_docs),1)

        print(similar_docs)

if __name__ == "__main__":
    unittest.main()