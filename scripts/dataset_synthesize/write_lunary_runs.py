import sys
sys.path.append("./")
from src.dataset_synthesize import lunary_handler
from src.mongodb_handler import MongoDBHandler
import os
from scripts.scripts_utils import get_config

if __name__ == "__main__":
    # TODO: maybe add here argparse    
    config = get_config(__file__)
    mongo_config = config.get("MongoDB")
    mongo_handler = MongoDBHandler.create_from_env_vars(mongo_config.get("db_name"))
    collection_name = mongo_config.get("collection_name")
    lunary_handler.write_to_db(collection_name,mongo_handler)