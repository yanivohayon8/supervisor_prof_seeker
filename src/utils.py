import json
import os

def load_json_settings(file_path:str,override_settings:dict=None):
    try:
        with open(file_path,"r") as f:
            settings = json.load(f)
    except FileNotFoundError as e:
        settings= {}

    if override_settings is None:
        override_settings = {}

    settings.update(override_settings)

    return settings

def load_chatbot_settings(file_path:str=None,override_settings:dict=None)->dict:
    if not file_path:
        file_path = os.path.join("src","chatbots","config.json")
    
    return load_json_settings(file_path,override_settings=override_settings)