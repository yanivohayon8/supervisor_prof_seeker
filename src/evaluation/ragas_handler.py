from ragas import EvaluationDataset
from src.mongodb_handler import MongoDBHandler  

USER_INPUT = "user_input"
RETRIEVED_CONTEXTS = "retrieved_contexts"
RESPONSE = "response"

def create_dataset_from_collection(mongo_handler: MongoDBHandler, collection_name: str) -> EvaluationDataset:
    projection = {
        USER_INPUT: True,
        RETRIEVED_CONTEXTS: True,
        RESPONSE: True,
        "_id": False  # hide internal MongoDB ID
    }
    mongo_docs = mongo_handler.read_all(collection_name, projection=projection)
    list_data = list(mongo_docs)

    if not list_data:
        raise ValueError(f"No documents found in collection '{collection_name}'")

    return EvaluationDataset.from_list(list_data)

def create_dataset_from_list(data: list[dict]) -> EvaluationDataset:
    '''For mocks'''
    if not data:
        raise ValueError("Dataset list is empty.")
    return EvaluationDataset.from_list(data)
