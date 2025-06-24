import unittest
from src.dataset_synthesize import lunary_handler
from src.mongodb_handler import MongoDBHandler
import json
import os
class TestLunaryHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_name = "test_lunary_handler"
        cls.collection_name = "test_lunary_handler"
        cls.mongo_handler = MongoDBHandler.create_from_env_vars(db_name=cls.db_name)
    
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
        lunary_handler.write_to_db(mongo_handler=self.mongo_handler)
        
if __name__ == "__main__":
    unittest.main()