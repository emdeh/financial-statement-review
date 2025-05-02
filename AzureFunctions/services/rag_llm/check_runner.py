"""
Module docstring.
"""

from services.rag_llm.checks import CHECKS
from services.rag_llm.retrieval_service import RetrievalService

def run_llm_checks(document_name: str) -> dict:
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
            k=chk.k
        )
        results[f"has_{chk.name}"]  = res["answer"].upper().startswith("YES")
        results[f"{chk.name}Pages"] = res["citations"]
    return results