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
                        This is what the LLM will be asked to answer.

        query (str):    The query to be used for the check.
                        This is what is used to search the index.
                        It is a 100% semantic-vector search, not a keyword search.
                        It should be a string that describes the content
                        you are looking for in the document.

        k (int):    The number of results to retrieve (default is 3).
                    This is the number of chunks to retrieve from the index
                    for the check based on the query.

        system_prompt (str, optional):  The system prompt to be used for the check.
    
    Notes:
    -----
        Checks must match the DocumentResult model in db_models.py.
        For example if you have `hasBalanceSheet` in the model, you musth have 
        BalanceSheet in the checks.py.

        `query` is what is used to search the index, and question is what is 
        asked of the LLM.

        Importantly, the `query` is a 100% semantic-vector search, not a 
        keyword search.
    """
    name: str
    field_name: str
    question: str
    query: str
    k: int = 3
    system_prompt: str = None
    scoring_profile: str = None
    scoring_parameters: list = None
    filter_patterns: list[str] = None
    include_patterns: list[str] = None

CHECKS = [
    CheckDef(
        name="Profit or Loss Statement",
        field_name="ProfitLoss",
        question="Does this doc contain a profit or loss statement in a tabulated format, comparring the current reporting period to the previous financial year? Sometimes referred to as a P&L or statement or other comphrensive income",
        query="profit or loss (P&L) statement"
    ),
    CheckDef(
        name="Balance Sheet",
        field_name="BalanceSheet",
        question="Does this doc contain a statement of changes in equity in a tabulated format, comparing the current reporting period to the previous financial year?",
        query="balance sheet"
    ),
    CheckDef(
        name="Cash Flow Statement",
        field_name="CashFlow",
        question="Does this doc contain a statement of cash flow in a tabulated format, comparing the current reporting period to the previous financial year?",
        query="cash flow statement"
    ),
    CheckDef(
    name="Going Concern",
    field_name="GoingConcern",
    question="""Does this doc actively state a material uncertainty or doubt about the company's ability to continue as a going concern? For example:
        - “The directors have significant doubt about the company's ability to continue…”
        - “Events cast material uncertainty over the entity's going concern assumption.”
        - “Current liabilities exceed current assets by $X, which may jeopardise continuity.”
    Return “No” for:
        - Boiler-plate language in the “Responsibilities of Directors/Auditor” section.
        - Any generic mention of the term “going concern.”
    Examples of boilerplate language:
        - "If we conclude that a material uncertainty exists, we are required to draw attention in our auditor's report to the related disclosures in the financial report or, if such disclosures are inadequate, to modify our opinion. Our conclusions are based on the audit evidence obtained up to the date of our auditor's report. However, future events or conditions may cause the Company to cease to continue as a going concern."
        """,
    query="significant doubt material uncertainty unable to continue foreseeable future",
    scoring_profile="materialUncertaintyBoost",
    scoring_parameters=["tags-material uncertainty,significant doubt,probable"],
    filter_patterns=[
            r"Responsibilities of Directors",
            r"Auditor's Responsibilities",
            r"Independent Audit Report to the members(?!.*Material Uncertainty)",
            r"Appendix"
        ],
    include_patterns=[
        r"material uncertainty related to the going concern"
        ]
    )
]
