import unittest
from src.indexing_pipeline import index_text_file
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TestIndexTextFile(unittest.TestCase):

    def test_indexing_dummy_abstract(self):
        file_path = "tests/data/2501.00836v2.txt"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2")
        vector_store = InMemoryVectorStore(embeddings)

        index_text_file(file_path,text_splitter,vector_store)

        query = "Ancient artworks are obtained in archaeological excavations."
        similar_docs = vector_store.similarity_search(query,k=2)

        self.assertEqual(len(similar_docs),2)

        print(similar_docs)


if __name__ == "__main__":
    unittest.main()