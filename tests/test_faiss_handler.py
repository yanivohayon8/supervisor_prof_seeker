import unittest
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from uuid import uuid4
from langchain_core.documents import Document
import os
import shutil

class TestFaissRun(unittest.TestCase):

    def test_tutorial_runs(self):
        embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2")
        
        index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        

        document_1 = Document(
            page_content="I had chocalate chip pancakes and scrambled eggs for breakfast this morning.",
            metadata={"source": "tweet"},
        )

        document_2 = Document(
            page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
            metadata={"source": "news"},
        )

        document_3 = Document(
            page_content="Building an exciting new project with LangChain - come check it out!",
            metadata={"source": "tweet"},
        )

        document_4 = Document(
            page_content="Robbers broke into the city bank and stole $1 million in cash.",
            metadata={"source": "news"},
        )

        document_5 = Document(
            page_content="Wow! That was an amazing movie. I can't wait to see it again.",
            metadata={"source": "tweet"},
        )

        documents = [
            document_1,
            document_2,
            document_3,
            document_4,
            document_5
        ]

        uuids = [str(uuid4()) for _ in range(len(documents))]

        vector_store.add_documents(documents=documents, ids=uuids)

        vector_store.delete(ids=[uuids[-1]])


        folder_path = "tests/data/temp_faiss_index"

        vector_store.save_local(folder_path)

        new_vector_store = FAISS.load_local(
            folder_path, embeddings, allow_dangerous_deserialization=True
        )

        docs = new_vector_store.similarity_search("qux")

        del new_vector_store

        shutil.rmtree(folder_path)