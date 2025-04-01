from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.utils import load_json_settings


class GeneratingPipeline:
    
    def __init__(self,config_path="src/generating_pipeline/config.json",override_settings:dict=None):
        total_settings = load_json_settings(config_path,override_settings=override_settings)

        self.vector_store_settings = total_settings.get("vector_store",{})
        
        if not "input_folder" in self.vector_store_settings.keys():
            raise ValueError(f"The input_folder under vector_store key in {config_path} is not specified")
        
        self.embeddings_settings = total_settings.get("embeddings",{})
        self.init_embeddings_(self.embeddings_settings)

        self.init_vector_store_(self.vector_store_settings)

    def init_embeddings_(self,settings:dict):
        ''' TODO: read the meta data (write it?) and then load the appropriate embedding'''

        supported_embeddings = {
            "HuggingFaceEmbeddings":HuggingFaceEmbeddings
        }
        embedding_type = settings.get("type","HuggingFaceEmbeddings")

        if not embedding_type in supported_embeddings:
            raise NotImplementedError(f"Currently, Pipeline do not support {embedding_type} embeddings")
        
        settings.pop("type",None)
        self.embeddings = supported_embeddings[embedding_type](**settings)

    def init_vector_store_(self,settings:dict):
        index_name = settings.get("index_name","index")
        allow_dangerous_deserialization = settings.get("allow_dangerous_deserialization",True)
        used_keys = ["type","input_folder","index_name","allow_dangerous_deserialization","dst_folder"]
        other_kwargs =  {k:v for k,v in settings.items() if not k in used_keys}

        self.vector_store = FAISS.load_local(
            folder_path=settings["input_folder"],embeddings=self.embeddings,
            index_name=index_name,
            allow_dangerous_deserialization=allow_dangerous_deserialization,
            **other_kwargs
        )
    
    def similarity_search(self,query:str,**kwargs):
        return self.vector_store.similarity_search(query,**kwargs)

    def augment_promt(self):
        pass

    def generate_response(self):
        pass