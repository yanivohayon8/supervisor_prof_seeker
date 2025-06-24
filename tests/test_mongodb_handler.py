import unittest
from pymongo.errors import ConnectionFailure
from src.mongodb_handler import MongoDBHandler

class TestMongoDBHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_name = "test_mongodb_handler_db"
        cls.collection_name = "test_collection"

        # Create handler using environment-based factory
        cls.handler = MongoDBHandler.create_from_env_vars(db_name=cls.db_name)

    @classmethod
    def tearDownClass(cls):
        # Drop the test DB to clean up
        cls.handler.client.drop_database(cls.db_name)

    def test_connection_ping(self):
        """Test that MongoDB connection is alive using ping command."""
        try:
            self.handler.client.admin.command('ping')
        except ConnectionFailure:
            self.fail("MongoDB ping failed — connection is down.")

    def test_insert_many_and_read(self):
        """Test inserting multiple documents and reading them back."""
        docs = [{"id": 1, "val": "a"}, {"id": 2, "val": "b"}]
        self.handler.insert_many(self.collection_name, docs)
        read_back = list(self.handler.db[self.collection_name].find({}, {"_id": 0}))
        self.assertIn({"id": 1, "val": "a"}, read_back)
        self.assertIn({"id": 2, "val": "b"}, read_back)

    def test_ensure_indexes(self):
        """Test index creation on specified fields."""
        self.handler.ensure_indexes(self.collection_name, [
            ("id", {"unique": True}),
            ("val", {})
        ])
        indexes = self.handler.db[self.collection_name].index_information()
        self.assertIn("id_1", indexes)
        self.assertTrue(indexes["id_1"].get("unique", False))
