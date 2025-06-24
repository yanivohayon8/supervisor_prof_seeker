import os
import yaml

def load_yaml(file_path:str)->dict:
    with open(file_path, "r") as file:
        config_data = yaml.safe_load(file)
        return config_data

def get_config(module_path:str)->dict:
    module_dir = os.path.dirname(module_path)
    yaml_path = os.path.join(module_dir,"config.yml")
    conf = load_yaml(yaml_path)
    module_name = os.path.basename(module_path).split(".")[0]

    return conf.get(module_name)

