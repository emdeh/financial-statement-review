"""
    services/rag_llm/check_runner.py
    Module for running RAG+LLM checks on documents.

    This module provides a function to run all RAG+LLM yes/no checks
    defined in the CHECKS list. It returns a flat dictionary of flags
    and citation lists for each check. The function uses the
    RetrievalService to perform the checks and retrieve citations.

    Functions:
    ---------
        run_llm_checks(): Runs all RAG+LLM yes/no checks and returns a
        dictionary of flags and citation lists.
"""

from services.rag_llm.checks import CHECKS
from services.rag_llm.retrieval_service import RetrievalService

def run_llm_checks(document_name: str, system_prompt: str = None) -> dict:
    """
    Runs all RAG+LLM yes/no checks and returns a dictionary of flags
    and citation lists.

    This function iterates over the CHECKS list, performs each check
    using the RetrievalService, and constructs a flat dictionary
    containing the results. The keys in the dictionary are formatted
    to match the expected field names in the Pydantic model.

    Args:
        document_name (str): The name of the document to be checked.
        system_prompt (str, optional): The system prompt to be used for
            the checks. If not provided, the default prompt from the
            CHECKS list will be used.

    Returns:
        dict: A dictionary containing the results of the checks.
            The keys are formatted as "has{FieldName}" for flags and
            "{field_name[0].lower()}{field_name[1:]}" for citation lists.
            For example, "hasProfitLoss" and "profitLossPages".

    Raises:
        None: This function does not raise any exceptions.
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
            system_prompt=system_prompt or chk.system_prompt,
            scoring_profile=chk.scoring_profile,
            scoring_parameters=chk.scoring_parameters,
            filter_patterns=chk.filter_patterns
        )
        # build the exact field names your Pydantic model expects:
        flag_key  = f"has{chk.field_name}" # e.g. "hasProfitLoss"
        pages_key = f"{chk.field_name[0].lower()}{chk.field_name[1:]}Pages"
        # ^ lower-camel for the Pages key, e.g. "profitLossPages"

        results[flag_key]  = res["answer"].upper().startswith("YES")
        results[pages_key] = res["citations"]
    return results
    