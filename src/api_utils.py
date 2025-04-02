import os
import getpass

from langchain_openai import OpenAIEmbeddings

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

