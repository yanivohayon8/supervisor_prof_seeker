import os
import getpass
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from lunary import LunaryCallbackHandler

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

def enable_langsmith_tracing():
    update_environment_variable_("LANGSMITH_TRACING","true")

def disable_langsmith_tracing_key():
    update_environment_variable_("LANGSMITH_TRACING","false")

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


def get_llm_langchain_openai(is_lunary_audit=False,lunary_handler_params:dict={}, **chat_settings):
    verify_openai_api_key()

    if is_lunary_audit:
        return get_langchain_openai_lunary_(handler_params=lunary_handler_params,**chat_settings)

    else:
        return ChatOpenAI(**chat_settings)


def get_langchain_openai_lunary_(handler_params:dict={},**chat_settings):
    verify_lunary_public_key()

    handler = LunaryCallbackHandler(handler_params)

    chat_settings.setdefault("callbacks",list())
    chat_settings["callbacks"].append(handler)

    llm = ChatOpenAI(
        **chat_settings
    )

    return llm

def verify_lunary_public_key():
    verify_environment_variable_("LUNARY_PUBLIC_KEY")

def verify_lunary_private_key():
    key_ = "LUNARY_PRIVATE_KEY"
    verify_environment_variable_(key_)

    return get_environment_variable_(key_)


def verify_and_get_environment_variable(name):
    verify_environment_variable_(name)

    return get_environment_variable_(name)