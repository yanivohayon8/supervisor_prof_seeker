import unittest
from src.chatbots import openevals_wrapper 


class TestOpenevalsWrapper(unittest.TestCase):

    def test_correctness_evaluator(self):
        llm_model="openai:o3-mini"
        inputs = "How much has the price of doodads changed in the past year?"
        outputs = "Doodads have increased in price by 10% in the past year."
        reference_outputs = "The price of doodads has decreased by 50% in the past year."

        eval_result = openevals_wrapper.evaluate_correctness(llm_model,inputs,outputs,reference_outputs=reference_outputs)
        self.assertFalse(eval_result["score"])
    
    def test_rag_helpfulness_evaluator(self):
        llm_model="openai:o3-mini"
        inputs = "Where was the first president of FoobarLand born?"
        outputs = "The first president of FoobarLand was Bagatur Askaryan."

        eval_result = openevals_wrapper.evaluate_rag_helpfulness(llm_model,inputs,outputs)
        self.assertFalse(eval_result["score"])



if __name__ == "__main__":
    unittest.main()