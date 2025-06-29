from src.mongodb_handler import MongoDBHandler
from src.api_utils import verify_lunary_private_key
import requests
import json
from src.evaluation.ragas_handler import USER_INPUT,RESPONSE,RETRIEVED_CONTEXTS

LUNARY_END_POINT = "https://api.lunary.ai/v1"
ALLOWED_LUNARY_TYPE_LLM_RUN_KEYS = {"id","projectId","feedback","parentFeedback","feedbacks","type","name","createdAt","endedAt","tokens","tags","metadata"} # "input","output"

def write_to_db(collection_name:str,mongo_handler:MongoDBHandler,error_collection_name:str=None):
    if not error_collection_name:
        error_collection_name = collection_name + "_errors"

    mongo_handler.ensure_indexes(collection_name, [
        ("id", {"unique": True}),
        ("createdAt", {})
    ])

    for runs in get_runs():
        docs = []
        error_docs = []

        for run in runs:
            try:
                processed_run = process_run_(run)
                docs.append(processed_run)
            except Exception as e:
                error_docs.append({**run,f"lunary_handler_error":str(e)})

        if docs:
            try:
                mongo_handler.insert_many(collection_name,docs, ordered=False) # 
            except Exception as e:
                print(f"Error inserting batch: {e}")
        
        if error_docs:
            try:
                mongo_handler.insert_many(error_collection_name,error_docs, ordered=False) # 
            except Exception as e:
                print(f"Error inserting error_docs batch: {e}")


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

def get_url_(*args):
    route = get_route_(*args)
    return LUNARY_END_POINT + route

def get_route_(*args):
    arguments = [""] + list(args)
    return "/".join(arguments)

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

def process_run_(run:dict)->dict:
    processed_run = {k: run[k] for k in ALLOWED_LUNARY_TYPE_LLM_RUN_KEYS if k in run}
                
    for message in run["input"]:
        if message["role"] == "system":                    
            if processed_run.get(RETRIEVED_CONTEXTS):
                ValueError("Found two system messages")

            processed_run[RETRIEVED_CONTEXTS] = get_context_(message["content"])
        
        if message["role"] == "user":
            if processed_run.get(USER_INPUT,None):
                raise ValueError(f"Two input messages of a user in run {run["id"]}")
            
            processed_run[USER_INPUT] = message["content"]
    
    if not RETRIEVED_CONTEXTS in processed_run.keys():
        raise ValueError("Didn't found retrieved context")

    if not run["output"].get("content"):
        raise ValueError("Did not found output of assistant")
    else:
        processed_run[RESPONSE] = run["output"]["content"]

    return processed_run


def get_context_(run_input:str):
    delimiter = "Context:\n"
    start_index = run_input.index(delimiter) + len(delimiter)
    return run_input[start_index:]


