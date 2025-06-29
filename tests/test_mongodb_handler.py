import unittest
from pymongo.errors import ConnectionFailure
from src.mongodb_handler import MongoDBHandler

class TestMongoDBHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_name = "test_mongodb_handler_db"
        cls.collection_name = "test_collection"

        # Create handler using environment-based factory
        cls.handler = MongoDBHandler.create_from_env_vars(cls.db_name)

    @classmethod
    def tearDownClass(cls):
        # Drop the test DB to clean up
        cls.handler.drop_database(cls.db_name)

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

    def test_read_all(self):
        """Test read_all returns all inserted documents."""
        docs = [{"id": 10, "val": "x"}, {"id": 11, "val": "y"}]
        self.handler.insert_many(self.collection_name, docs)
        results = list(self.handler.read_all(self.collection_name, projection={"_id": 0}))
        self.assertIn({"id": 10, "val": "x"}, results)
        self.assertIn({"id": 11, "val": "y"}, results)

    def test_read_with_query_and_projection(self):
        """Test read returns filtered documents with correct projection."""
        docs = [{"id": 100, "val": "secret", "flag": True}, {"id": 101, "val": "secret", "flag": False}]
        self.handler.insert_many(self.collection_name, docs)
        query = {"flag": True}
        projection = {"_id": 0, "id": 1}
        results = list(self.handler.read(query, self.collection_name, projection))
        self.assertEqual(results, [{"id": 100}])

