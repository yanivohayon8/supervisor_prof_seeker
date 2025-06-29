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

def load_jsonl_to_dict_list(filepath):
    """
    Generator that yields one JSON object (as a dict) at a time from a JSONL file.
    
    Args:
        filepath (str): Path to the .jsonl file.
        
    Yields:
        dict: The next JSON object from the file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)