import unittest
from src.indexing_pipeline.indexing_pipeline import index_pdf_paper,index_text_file,IndexingPipeline
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import faiss
from langchain_community.docstore import InMemoryDocstore
import shutil
import os

class TestIndexTextFile(unittest.TestCase):

    def test_index_text_file(self):
        file_path = "tests/data/2501.00836v2.txt"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2")
        vector_store = InMemoryVectorStore(embeddings)

        index_text_file(file_path,text_splitter,vector_store)

        query = "Ancient artworks are obtained in archaeological excavations."
        similar_docs = vector_store.similarity_search(query,k=2)

        self.assertEqual(len(similar_docs),2)

        print(similar_docs)


    def test_index_pdf_InMemoryVectorStore(self):
        file_path = "tests/data/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2")
        vector_store = InMemoryVectorStore(embeddings)

        index_pdf_paper(file_path,text_splitter,vector_store)

        query = "Ancient artworks are obtained in archaeological excavations."
        similar_docs = vector_store.similarity_search(query,k=2)

        self.assertEqual(len(similar_docs),2)

        print(similar_docs)

    def test_index_pdf_faiss_1(self):
        file_path = "tests/data/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2")
        vector = embeddings.embed_query("hello world")
        index = faiss.IndexFlatL2(len(vector))
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
            )

        index_pdf_paper(file_path,text_splitter,vector_store)

        query = "Ancient artworks are obtained in archaeological excavations."
        similar_docs = vector_store.similarity_search(query,k=2)

        self.assertEqual(len(similar_docs),2)

        print(similar_docs)


class TestPipeline(unittest.TestCase):
    def test_default(self):
        file_path = "tests/data/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"

        settings = {
            "vector_store":{
                "type":"InMemoryVectorStore"
            }
        }

        pipeline = IndexingPipeline(override_settings=settings)
        pipeline.run([file_path])

    def test_faiss_1(self):
        file_path = "tests/data/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"
        
        settings = {
            "vector_store":{
                "type":"FAISS"
            }
        }

        pipeline = IndexingPipeline(override_settings=settings)
        pipeline.run([file_path])
    
    def test_faiss_save_db(self):
        file_path = "tests/data/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"
        dst_folder = "tests/tmp/faiss_vector_db"

        settings = {
            "vector_store":{
                "type":"FAISS",
                "dst_folder": dst_folder
            }
        }

        pipeline = IndexingPipeline(override_settings=settings)
        pipeline.run([file_path])

        if os.path.exists(dst_folder):
            shutil.rmtree(dst_folder)

if __name__ == "__main__":
    unittest.main()