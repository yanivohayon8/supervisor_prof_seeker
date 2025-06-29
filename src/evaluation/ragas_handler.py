from ragas import EvaluationDataset, evaluate as ragas_evaluate
from src.mongodb_handler import MongoDBHandler  
from src.api_utils import get_llm_langchain_openai
from typing import Optional, List, Dict
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    LLMContextRecall,
    Faithfulness,
    FactualCorrectness,
)
from ragas.metrics.base import Metric
from langchain_core.language_models.base import BaseLanguageModel


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


class RagEvaluator:

    _SUPPORTED_METRICS: Dict[str, Metric] = {
        "context_recall": LLMContextRecall(),
        "faithfulness": Faithfulness(),
        "factual_correctness": FactualCorrectness(),
    }

    def __init__(self,dataset: EvaluationDataset,llm: Optional[BaseLanguageModel] = None):
        self.dataset = dataset
        self.llm = LangchainLLMWrapper(llm or self._get_default_llm())

    def _get_default_llm(self) -> BaseLanguageModel:        
        return get_llm_langchain_openai(is_lunary_audit=False)

    def evaluate(self,metric_names: Optional[List[str]] = None):
        if metric_names is None:
            metrics = list(self._SUPPORTED_METRICS.values())
        else:
            unknown = set(metric_names) - set(self._SUPPORTED_METRICS)
            if unknown:
                raise ValueError(f"Unsupported metrics requested: {', '.join(unknown)}")
            metrics = [self._SUPPORTED_METRICS[name] for name in metric_names]

        return ragas_evaluate(dataset=self.dataset,metrics=metrics,llm=self.llm)