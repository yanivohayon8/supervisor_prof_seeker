from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter
from langchain_core.vectorstores import InMemoryVectorStore,VectorStore
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from src import pdf_handler
from src.utils import load_json_settings
from src.api_utils import init_embeddings
import os
from src.vector_store_loaders.faiss_loader import load_vector_store,init_faiss

class IndexingPipeline():

    def __init__(self,config_path="src/indexing_pipeline/config.json",override_settings:dict=None):
        self.config_path = config_path
        self.total_settings = load_json_settings(config_path,override_settings=override_settings)

        self.text_splitter_settings = self.total_settings.get("text_splitter",{})
        self.init_text_splitter_()
        
        self.embeddings_settings = self.total_settings.get("embedding",{})
        embedding_type = self.embeddings_settings.pop("type",None)
        self.embeddings = init_embeddings(embedding_type,self.embeddings_settings)

        self.init_vector_store_()
        
    
    def init_text_splitter_(self):
        supported_splitters = {
            "RecursiveCharacterTextSplitter": RecursiveCharacterTextSplitter,
        }

        spliter_type = self.text_splitter_settings.get("type","RecursiveCharacterTextSplitter") #
        
        if  not spliter_type in supported_splitters:
            raise NotImplementedError(f"Currently, Pipeline do not support {spliter_type} text splitter")

        self.text_splitter_settings.pop("type",None)
        self.text_splitter = supported_splitters[spliter_type](**self.text_splitter_settings)

    def init_vector_store_(self):
        self.vector_store_settings  = self.total_settings.get("vector_store")
        vector_store_type = self.vector_store_settings.pop("type","InMemoryVectorStore") 
        
        if vector_store_type == "InMemoryVectorStore":
            self.vector_store = InMemoryVectorStore(self.embeddings)
        elif vector_store_type == "FAISS":
            input_folder = self.vector_store_settings.get("input_folder",None)

            if input_folder and os.path.exists(input_folder):
                self.vector_store = load_vector_store(self.embeddings,self.vector_store_settings)
            else:
                # settings.pop("type",None)
                self.vector_store = init_faiss(self.embeddings)
                
        else:
            raise NotImplementedError(f"Currently, Pipeline does not support vector store {vector_store_type}")

    def run(self,pdf_files:list[str]):
        for pdf in pdf_files:
            try:
                print(f"Indexing {pdf}")
                index_pdf_paper(pdf,self.text_splitter,self.vector_store)
            except Exception as e:
                print(f"Failed to index {pdf}: {e}")

        if isinstance(self.vector_store,FAISS):
            save_folder = self.vector_store_settings.get("save_folder",None)

            if save_folder:
                self.vector_store.save_local(save_folder)


def index_pdf_paper(pdf_path:str,text_splitter:TextSplitter,vector_store:VectorStore):
    text = pdf_handler.read_pdf(pdf_path)
    abstract = pdf_handler.extract_absract(text)
    intro = pdf_handler.extract_introduction(text)

    page_content = abstract+ " " + intro

    doc = Document(
        page_content=page_content,
        metadata={
            "sections":["abstract","introduction"],
            "input_file":pdf_path
            }
        )

    docs = [doc]

    all_splits = text_splitter.split_documents(docs)
    vector_store.add_documents(documents=all_splits)

def index_text_file(file_path:str,text_splitter:TextSplitter, vector_store:VectorStore):
    loader = TextLoader(file_path)
    docs = loader.load()
    all_splits = text_splitter.split_documents(docs)
    _ = vector_store.add_documents(documents=all_splits)
  