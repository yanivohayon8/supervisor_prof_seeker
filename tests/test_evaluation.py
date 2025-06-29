import unittest
from src.evaluation import lunary_handler,ragas_handler
from src.mongodb_handler import MongoDBHandler
import json
import os
from ragas import EvaluationDataset

from unittest.mock import patch, MagicMock

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




class TestRagEvaluator(unittest.TestCase):
    def setUp(self):
        sample = [{
            ragas_handler.USER_INPUT: "What is the capital of France?",
            ragas_handler.RETRIEVED_CONTEXTS: ["Paris is the capital of France."],
            ragas_handler.RESPONSE: "The capital of France is Paris.",
            "reference": "Paris"
        }]
        self.fake_dataset = EvaluationDataset.from_list(sample)

    # @patch("src.api_utils.get_llm_langchain_openai")
    # @patch("src.rag_evaluator.evaluate")
    # def test_evaluate_with_default_metrics(self, mock_evaluate, mock_get_llm):
    #     """Test evaluate() with default metric set."""
    #     mock_evaluate.return_value = {"faithfulness": 0.7}
    #     mock_get_llm.return_value = MagicMock(name="FakeLLM")

    #     evaluator = ragas_handler.RagEvaluator(dataset=self.fake_dataset)
    #     result = evaluator.evaluate()

    #     mock_evaluate.assert_called_once()
    #     args, kwargs = mock_evaluate.call_args

    #     self.assertEqual(kwargs["dataset"], self.fake_dataset)
    #     self.assertTrue("metrics" in kwargs)
    #     self.assertTrue("llm" in kwargs)
    #     self.assertEqual(result, {"faithfulness": 0.7})

    # @patch("src.rag_evaluator.get_llm_langchain_openai")
    # @patch("src.rag_evaluator.evaluate")
    # def test_evaluate_with_specific_metrics(self, mock_evaluate, mock_get_llm):
    #     """Test evaluate() with specific metric names."""
    #     mock_evaluate.return_value = {"factual_correctness": 0.9}
    #     mock_get_llm.return_value = MagicMock(name="FakeLLM")

    #     evaluator = ragas_handler.RagEvaluator(dataset=self.fake_dataset)
    #     result = evaluator.evaluate(metric_names=["factual_correctness"])

    #     called_metrics = mock_evaluate.call_args[1]["metrics"]
    #     self.assertEqual(len(called_metrics), 1)
    #     self.assertEqual(result, {"factual_correctness": 0.9})

    # @patch("src.rag_evaluator.get_llm_langchain_openai")
    # def test_invalid_metric_raises_error(self, mock_get_llm):
    #     """Test that unsupported metric names raise ValueError."""
    #     mock_get_llm.return_value = MagicMock(name="FakeLLM")
    #     evaluator = ragas_handler.RagEvaluator(dataset=self.fake_dataset)

    #     with self.assertRaises(ValueError) as context:
    #         evaluator.evaluate(metric_names=["not_a_real_metric"])

    #     self.assertIn("Unsupported metrics requested", str(context.exception))


if __name__ == "__main__":
    unittest.main()