from pymongo import MongoClient
from src.api_utils import verify_and_get_environment_variable

class MongoDBHandler:
    def __init__(self, uri:str, db_name:str):
        self.client = MongoClient(uri)
        self.db_name = db_name or self._get_first_database_name()
        self.db = self.client[self.db_name]


    def _get_first_database_name(self):
        dbs = self.client.list_database_names()
        if not dbs:
            raise ValueError("No databases found on MongoDB server.")
        return dbs[0]

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
        collection = self.db[collection_name]
        collection.insert_many(documents, **kwargs)

    def ensure_indexes(self, collection_name, indexes):
        """
        indexes: List of (field, kwargs) tuples.
        e.g., [("id", {"unique": True}), ("createdAt", {})]
        """
        collection = self.db[collection_name]
        for field, options in indexes:
            collection.create_index(field, **options)

    def drop_database(self,db_name:str):
        self.client.drop_database(db_name)
