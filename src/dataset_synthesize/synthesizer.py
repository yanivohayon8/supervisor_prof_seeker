from src.utils import load_jsonl_to_dict_list
from src.api_utils import verify_lunary_private_key
from src.consts import LUNARY_DATASET_PATH
import requests
import json

def read_dataset_from_file_(jsonl_path=LUNARY_DATASET_PATH):
    return load_jsonl_to_dict_list(jsonl_path)


LUNARY_END_POINT = "https://api.lunary.ai/v1"

def get_runs():
    url = get_url_("runs")
    response = http_get_lunary_(url)
    content_str = convert_bytes_to_str(response.content)
    content = json.loads(content_str)
    runs = content.get("data",[])

    while len(runs) > 0:
        yield runs

        page=content.get("page")+1
        response = http_get_lunary_(url,params={"page":page})
        content_str = convert_bytes_to_str(response.content)
        content = json.loads(content_str)
        runs = content.get("data",[])

def get_route_(*args):
    arguments = [""] + list(args)
    return "/".join(arguments)

def get_url_(*args):
    route = get_route_(*args)
    return LUNARY_END_POINT + route

def http_get_lunary_(url,  params=None, headers=None):
    token = verify_lunary_private_key()
    auth_header = {'Authorization': f'Bearer {token}'}

    if headers:
        headers.update(auth_header)
    else:
        headers = auth_header

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)

    return response

def convert_bytes_to_str(data:bytes,decoding="utf-8"):
    return data.decode(decoding)


def read_dataset(file_path:str=None):
    pass

def get_runs_export_deprecated_(query_type="thread",export_format="jsonl"):
    '''
        View the parameters options
        https://docs.lunary.ai/api-reference/runs/export-runs-data
    '''
    params = {
        "type":query_type,
        "exportFormat":export_format
    }

    response = http_get_lunary_(LUNARY_END_POINT,params=params)

    content = response.content.decode("utf-8")

    for line in content.splitlines():
        if line.strip():
            data =  json.loads(line)
            yield data
