"""
services/rag_llm/checks.py
Module for defining RAG+LLM checks on documents.

This module defines a list of checks to be performed on documents
using the RAG+LLM approach. Each check is represented by a
CheckDef object, which includes the check name, field name,
question, query, and other parameters. The checks are used to
determine the presence of specific financial statements
in the documents, such as profit and loss statements,
balance sheets, and cash flow statements.

Classes:
--------
    CheckDef: A class representing a check definition for RAG+LLM checks.
    CHECKS: A list of CheckDef objects representing the checks to be performed.

"""
from dataclasses import dataclass

@dataclass
class CheckDef:
    """
    A class representing a check definition for RAG+LLM checks.
    This class includes the check name, field name, question,
    query, and other parameters.

    Attributes:
    ----------
        name (str): The name of the check.
        field_name (str): The field name in the Pydantic model.
        question (str): The question to be asked for the check.
        query (str): The query to be used for the check.
        k (int): The number of results to retrieve (default is 3).
        system_prompt (str, optional): The system prompt to be used for the check.
    
    Notes:
    -----
        Checks must much the DocumentResult model in db_models.py.
        For example if you have `hasBalanceSheet` in the model, you musth have 
        BalanceSheet in the checks.py.
    """
    name: str
    field_name: str
    question: str
    query: str
    k: int = 3
    system_prompt: str = None

CHECKS = [
    CheckDef(
        name="Profit or Loss Statement",
        field_name="ProfitLoss",
        question="Does this doc contain a profit or loss statement?",
        query="profit or loss statement"
    ),
    CheckDef(
        name="Balance Sheet",
        field_name="BalanceSheet",
        question="Does this doc contain a balance sheet?",
        query="balance sheet"
    ),
    CheckDef(
        name="Cash Flow Statement",
        field_name="CashFlow",
        question="Does this doc contain a cash flow statement?",
        query="cash flow statement"
    ),
]

