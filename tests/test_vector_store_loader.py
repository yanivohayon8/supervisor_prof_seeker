import unittest
from src.vector_store_loaders.faiss_loader import load_faiss,init_faiss,save_faiss
from src.api_utils import init_openai_embeddings_


class TestInitFAISS(unittest.TestCase):

    def test_init_faiss(self):
        embeddings = init_openai_embeddings_("text-embedding-3-small")
        vector_store= init_faiss(embeddings)
        # save_faiss(vector_store, "./faiss_openai_text-embedding-3-small")

    def test_loading_faiss(self):
        vector_store = load_faiss()

        query = "Ancient artworks are obtained in archaeological excavations."
        similar_docs = vector_store.similarity_search(query,k=2)

        self.assertEqual(len(similar_docs),2)

        print(similar_docs)

if __name__ == "__main__":
    unittest.main()