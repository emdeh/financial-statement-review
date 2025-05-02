"""
Module docstring.
"""
from dataclasses import dataclass

@dataclass
class CheckDef:
    """
    Class docstring.
    """
    name: str
    question: str
    query: str
    k: int = 3
    system_prompt: str = None

CHECKS = [
    CheckDef(
        name="Profit or Loss Statement",
        question="Does this doc contain a profit or loss statement?",
        query="profit or loss statement"
    ),
    CheckDef(
        name="Balance Sheet",
        question="Does this doc contain a balance sheet?",
        query="balance sheet"
    ),
    CheckDef(
        name="Cash Flow Statement",
        question="Does this doc contain a cash flow statement?",
        query="cash flow statement"
    ),
]