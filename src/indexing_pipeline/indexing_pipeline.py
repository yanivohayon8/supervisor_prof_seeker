from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore,VectorStore
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
import faiss
from langchain_community.docstore import InMemoryDocstore
from src import pdf_handler
from src.utils import load_json_settings


class IndexingPipeline():

    def __init__(self,config_path="src/indexing_pipeline/config.json",override_settings:dict=None):
        total_settings = load_json_settings(config_path,override_settings=override_settings)

        self.text_splitter_settings = total_settings.get("text_splitter",{})
        self.init_text_splitter_(self.text_splitter_settings)
        
        self.embeddings_settings = total_settings.get("embeddings",{})
        self.init_embeddings_(self.embeddings_settings)
        
        self.vector_store_settings = total_settings.get("vector_store",{})
        self.init_vector_store_(self.vector_store_settings)
        
    
    def init_text_splitter_(self,settings:dict):
        supported_splitters = {
            "RecursiveCharacterTextSplitter": RecursiveCharacterTextSplitter,
        }

        spliter_type = settings.get("type","RecursiveCharacterTextSplitter") #
        
        if  not spliter_type in supported_splitters:
            raise NotImplementedError(f"Currently, Pipeline do not support {spliter_type} text splitter")

        settings.pop("type",None)
        self.text_splitter = supported_splitters[spliter_type](**settings)

    def init_embeddings_(self,settings:dict):
        supported_embeddings = {
            "HuggingFaceEmbeddings":HuggingFaceEmbeddings
        }
        embedding_type = settings.get("type","HuggingFaceEmbeddings")

        if not embedding_type in supported_embeddings:
            raise NotImplementedError(f"Currently, Pipeline do not support {embedding_type} embeddings")
        
        settings.pop("type",None)
        self.embeddings = supported_embeddings[embedding_type](**settings)

    def init_vector_store_(self,settings:dict):
        vector_store_type = settings.get("type","InMemoryVectorStore") 
        
        if vector_store_type == "InMemoryVectorStore":
            self.vector_store = InMemoryVectorStore(self.embeddings)
        elif vector_store_type == "FAISS":
            
            input_folder = settings.get("input_folder",None)

            if input_folder:
                index_name = settings.get("index_name","index")
                allow_dangerous_deserialization = settings.get("allow_dangerous_deserialization",True)
                used_keys = ["type","input_folder","index_name","allow_dangerous_deserialization","dst_folder"]
                other_kwargs =  {k:v for k,v in settings.items() if not k in used_keys}

                self.vector_store = FAISS.load_local(
                    folder_path=input_folder,embeddings=self.embeddings,
                    index_name=index_name,
                    allow_dangerous_deserialization=allow_dangerous_deserialization,
                    **other_kwargs
                    )
            else:
                settings.pop("type",None)
                # del settings["input_folder"]

                vector = self.embeddings.embed_query("hello world")
                index = faiss.IndexFlatL2(len(vector))
                self.vector_store = FAISS(
                    embedding_function=self.embeddings,
                    index=index,
                    docstore=InMemoryDocstore(),
                    index_to_docstore_id={}
                    )
        else:
            raise NotImplementedError(f"Currently, Pipeline does not support vector store {vector_store_type}")

    def run(self,pdf_files:list[str]):
        for pdf in pdf_files:
            try:
                index_pdf_paper(pdf,self.text_splitter,self.vector_store)
            except Exception as e:
                print(f"Failed to index {pdf}: {e}")

        if isinstance(self.vector_store,FAISS):
            dst_folder = self.vector_store_settings.get("dst_folder",None)

            if dst_folder:
                self.vector_store.save_local(dst_folder)


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
  