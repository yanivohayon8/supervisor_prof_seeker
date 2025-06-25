import unittest
from src.evaluation import lunary_handler,ragas_handler
from src.mongodb_handler import MongoDBHandler
import json
import os
from ragas import EvaluationDataset
class TestLunaryHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_name = "test_lunary_handler"
        cls.collection_name = "test_lunary_handler"
        cls.mongo_handler = MongoDBHandler.create_from_env_vars(cls.db_name)
    
    @classmethod
    def tearDownClass(cls):
        cls.mongo_handler.drop_database(cls.db_name)

    def test_get_url(self):
        url = lunary_handler.get_url_("runs")
        self.assertTrue(url.endswith("/runs"))

    def test_get_runs_compiles(self):
        pages = 0
        result = []

        for runs in lunary_handler.get_runs():
            self.assertIsInstance(runs,list)
            self.assertGreater(len(runs),0)
            pages+=1
            result = result + runs
        
        self.assertGreater(pages,0)
        tmp_path ="tests/tmp/lunary_dataset_updated.json"
        
        with open(tmp_path,"w") as f:
            json.dump(result,f)
        
        bytes_size = os.path.getsize(tmp_path)
        mb = bytes_size/1000/1000
        print(f"The rough size of dataset in lunary is {mb} MB")

        self.assertGreater(mb,0)

        os.remove(tmp_path)

    def test_write_to_db(self):
        lunary_handler.write_to_db(self.collection_name,mongo_handler=self.mongo_handler)
        
class TestRagasHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_name = "evaluation"
        cls.collection_name = "test_ragas_handler"
        cls.mongo_handler = MongoDBHandler.create_from_env_vars(cls.db_name)

        # Seed the test collection with documents
        cls.seed_data = [
            {
                ragas_handler.USER_INPUT: "What is Python?",
                ragas_handler.RETRIEVED_CONTEXTS: ["Python is a programming language.","Java is a programming language."],
                ragas_handler.RESPONSE: "Python is a general-purpose language.",
            },
            {
                ragas_handler.USER_INPUT: "What is MongoDB?",
                ragas_handler.RETRIEVED_CONTEXTS: ["MongoDB is a NoSQL database.","MySQL is a NoSQL database."],
                ragas_handler.RESPONSE: "MongoDB stores data in documents.",
            }
        ]
        cls.mongo_handler.insert_many(cls.collection_name, cls.seed_data)

    @classmethod
    def tearDownClass(cls):
        cls.mongo_handler.get_collection_(cls.collection_name).drop()

    def test_create_dataset_from_list(self):
        sample_list = [
            {
                ragas_handler.USER_INPUT: "Hi",
                ragas_handler.RETRIEVED_CONTEXTS: ["Hello!"],
                ragas_handler.RESPONSE: "Goodbye",
                "reference": "Empty ref"
            }
        ]
        dataset = ragas_handler.create_dataset_from_list(sample_list)
        self.assertIsInstance(dataset, EvaluationDataset)
        self.assertEqual(len(dataset), 1)

    def test_create_dataset_from_collection(self):
        dataset = ragas_handler.create_dataset_from_collection(
            self.mongo_handler, self.collection_name
        )
        self.assertIsInstance(dataset, EvaluationDataset)
        self.assertGreaterEqual(len(dataset), 2)



if __name__ == "__main__":
    unittest.main()