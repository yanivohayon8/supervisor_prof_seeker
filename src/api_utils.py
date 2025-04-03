import os
import getpass

from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


def update_environment_variable_(name,val):
    os.environ[name] = val

def get_environment_variable_(name):
    return os.environ.get(name)

def verify_environment_variable_(name,message=None):
    if not get_environment_variable_(name):
        if message is None:
            message = f"Enter value for {name}:"

        update_environment_variable_(name,getpass.getpass(message))

def verify_openai_api_key():
    verify_environment_variable_("OPENAI_API_KEY")

def init_openai_embeddings_(model:str):
    verify_openai_api_key()
    return OpenAIEmbeddings(model=model)

def init_embeddings(embedding_type,settings:dict):
    supported_embeddings = {
        "HuggingFaceEmbeddings":HuggingFaceEmbeddings,
        "OpenAIEmbeddings": init_openai_embeddings_
    }

    if not embedding_type in supported_embeddings:
        raise NotImplementedError(f"Currently, Pipeline do not support {embedding_type} embeddings")
    
    return supported_embeddings[embedding_type](**settings)