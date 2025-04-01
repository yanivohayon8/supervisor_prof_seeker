from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import TextSplitter 
from langchain_core.vectorstores import VectorStore

def load_docs_from_text_(file_path):
    loader = TextLoader(file_path)
    docs = loader.load()

    return docs

def index_text_file(file_path:str,text_splitter:TextSplitter, vector_store:VectorStore):
    docs = load_docs_from_text_(file_path)
    all_splits = text_splitter.split_documents(docs)
    _ = vector_store.add_documents(documents=all_splits)

