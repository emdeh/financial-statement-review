"""
Module docstring.
"""

from services.rag_llm.checks import CHECKS
from services.rag_llm.retrieval_service import RetrievalService

def run_llm_checks(document_name: str, system_prompt: str = None) -> dict:
    """
    Runs all RAG+LLM yes/no checks defined in CHECKS,
    returning a flat dict of flags and citation lists.
    """
    retrieval = RetrievalService()
    results = {}
    for chk in CHECKS:
        res = retrieval.ask_with_citations(
            document_name=document_name,
            check_name=chk.name,
            question=chk.question,
            query=chk.query,
            k=chk.k,
            system_prompt=system_prompt or chk.system_prompt
        )
        # build the exact field names your Pydantic model expects:
        flag_key  = f"has{chk.field_name}" # e.g. "hasProfitLoss"
        pages_key = f"{chk.field_name[0].lower()}{chk.field_name[1:]}Pages"
        # ^ lower-camel for the Pages key, e.g. "profitLossPages"

        results[flag_key]  = res["answer"].upper().startswith("YES")
        results[pages_key] = res["citations"]
    return results