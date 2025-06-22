from src.utils import load_jsonl_to_dict_list
from src.consts import LUNARY_DATASET_PATH

def read_dataset_from_file_(jsonl_path=LUNARY_DATASET_PATH):
    return load_jsonl_to_dict_list(jsonl_path)

def read_dataset():
    pass
