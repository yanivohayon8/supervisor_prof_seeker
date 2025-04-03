import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from src.utils import load_json_settings
from src.api_utils import init_embeddings


def load_vector_store(embeddings,settings:dict):
    index_name = settings.get("index_name","index")
    allow_dangerous_deserialization = settings.get("allow_dangerous_deserialization",True)
    used_keys = ["type","input_folder","index_name","allow_dangerous_deserialization","save_folder"]
    other_kwargs =  {k:v for k,v in settings.items() if not k in used_keys}

    vector_store = FAISS.load_local(
        folder_path=settings["input_folder"],embeddings=embeddings,
        index_name=index_name,
        allow_dangerous_deserialization=allow_dangerous_deserialization,
        **other_kwargs
    )

    return vector_store


def load_faiss_indexed(config_path="src/indexing_pipeline/config.json",override_settings:dict=None):
    total_settings = load_json_settings(config_path,override_settings=override_settings)
    vector_store_settings = total_settings.get("vector_store",{})
    
    if not "input_folder" in vector_store_settings.keys():
        raise ValueError(f"The input_folder under vector_store key is not specified")
    
    embeddings_settings = total_settings.get("embedding",{})
    embedding_type = embeddings_settings.pop("type",None)
    embeddings = init_embeddings(embedding_type,embeddings_settings)

    vector_store = load_vector_store(embeddings, vector_store_settings)

    return vector_store

def init_faiss(embeddings):
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    return vector_store

def save_faiss(vector_store, save_path):
    vector_store.save_local(save_path)