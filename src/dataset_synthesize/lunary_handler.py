from src.mongodb_handler import MongoDBHandler
from src.api_utils import verify_lunary_private_key
import requests
import json

LUNARY_END_POINT = "https://api.lunary.ai/v1"
ALLOWED_LUNARY_TYPE_LLM_RUN_KEYS = {"id","projectId","feedback","parentFeedback","feedbacks","type","name","createdAt","endedAt","tokens","tags","input","output","metadata"}

def write_to_db(collection_name:str,mongo_handler:MongoDBHandler):
    mongo_handler.ensure_indexes(collection_name, [
        ("id", {"unique": True}),
        ("createdAt", {})
    ])

    for runs in get_runs():
        filtered_runs = [
            {k: run[k] for k in ALLOWED_LUNARY_TYPE_LLM_RUN_KEYS if k in run}
            for run in runs
        ]
        if filtered_runs:
            try:
                mongo_handler.insert_many(collection_name,filtered_runs, ordered=False) # 
            except Exception as e:
                print(f"Error inserting batch: {e}")


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