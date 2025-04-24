from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT,RAG_HELPFULNESS_PROMPT,RAG_GROUNDEDNESS_PROMPT

CORRECTNESS_FEEDBACK_KEY="correctness"

def evaluate_correctness(llm_model:str, inputs:str,outputs:str,reference_outputs:str=None):
    evaluator = correctness_evaluator_(llm_model)
    eval_result = apply_correctness_evaluator_(evaluator,inputs,outputs,reference_outputs=reference_outputs)

    return eval_result

# This could be called to langsmith without explicitly calling applying. look here at last code snippet https://docs.smith.langchain.com/evaluation
def correctness_evaluator_(llm_model:str):
    evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        feedback_key=CORRECTNESS_FEEDBACK_KEY,
        model=llm_model
    )

    return evaluator

def apply_correctness_evaluator_(evaluator,inputs:str,outputs:str,reference_outputs:str=None):
    if not reference_outputs:
        reference_outputs = ""
    
    eval_result = evaluator(
            inputs=inputs,
            outputs=outputs,
            reference_outputs=reference_outputs
        )
    
    return eval_result


    
RAG_HELPFULNESS_FEEDBACK_KEY="rag_helpfulness"

# This could be called to langsmith without explicitly calling applying. look here at last code snippet https://docs.smith.langchain.com/evaluation
def rag_helpfulness_evaluator_(llm_model:str):
    evaluator = create_llm_as_judge(
        prompt=RAG_HELPFULNESS_PROMPT,
        feedback_key=RAG_HELPFULNESS_FEEDBACK_KEY,
        model=llm_model
    )

    return evaluator

def apply_rag_helpfulness_evaluator_(evaluator,question:str,answer:str):
    inputs ={"question":question,}
    outputs = {"answer":answer}
    
    eval_result = evaluator(
        inputs=inputs,
        outputs=outputs,
    )
    
    return eval_result

def evaluate_rag_helpfulness(llm_model:str, inputs:str,outputs:str):
    evaluator = rag_helpfulness_evaluator_(llm_model)
    eval_result = apply_rag_helpfulness_evaluator_(evaluator,inputs,outputs)

    return eval_result

RAG_GROUNDEDNESS_FEEDBACK_KEY = "rag_groundness"

def rag_groundeness_evaluator_(llm_model:str):
    evaluator = create_llm_as_judge(
        prompt=RAG_GROUNDEDNESS_PROMPT,
        feedback_key=RAG_GROUNDEDNESS_FEEDBACK_KEY,
        model=llm_model
    )

    return evaluator

def apply_rag_groundeness_evaluator_(evaluator,context_documents:list[str],answer:str):
    context = {
        "documents": context_documents,
    }

    outputs = {
        "answer": answer,
    }
    
    eval_result = evaluator(
        context=context,
        outputs=outputs,
    )
    
    return eval_result

def evaluate_rag_groundeness(llm_model:str, context_documents:list[str],answer:str):
    evaluator = rag_groundeness_evaluator_(llm_model)
    eval_result = apply_rag_groundeness_evaluator_(evaluator,context_documents,answer)

    return eval_result