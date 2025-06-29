from pymongo import MongoClient
from src.api_utils import verify_and_get_environment_variable

class MongoDBHandler:
    def __init__(self, uri:str, db_name:str):
        self.client = MongoClient(uri)
        self.db_name = db_name
        self.db = self.client[self.db_name]

    @classmethod
    def create_from_env_vars(cls,db_name:str,**kwargs):
        username = verify_and_get_environment_variable("MongoDBUsername")
        password = verify_and_get_environment_variable("MongoDBPassword")
        host = verify_and_get_environment_variable("MongoDBHost")

        uri = cls.get_uri_(username,password,host)

        return cls(uri,db_name,**kwargs)

    @classmethod
    def get_uri_(cls,username:str,password:str,host:str):
        return f"mongodb+srv://{username}:{password}@{host}"

    def insert_many(self, collection_name, documents, **kwargs):
        if not documents:
            return
        collection = self.get_collection_(collection_name)
        collection.insert_many(documents, **kwargs)
    
    def get_collection_(self,collection_name):
        return self.db[collection_name]

    def ensure_indexes(self, collection_name, indexes):
        """
        indexes: List of (field, kwargs) tuples.
        e.g., [("id", {"unique": True}), ("createdAt", {})]
        """
        collection = self.get_collection_(collection_name)
        for field, options in indexes:
            collection.create_index(field, **options)

    def drop_database(self,db_name:str):
        self.client.drop_database(db_name)

    def read_all(self, collection_name: str, projection: dict = None):
        collection = self.get_collection_(collection_name)
        return collection.find({}, projection or {})

    def read(self, query: dict, collection_name: str, projection: dict = None):
        collection = self.get_collection_(collection_name)
        return collection.find(query, projection or {})
