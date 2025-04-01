import json


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