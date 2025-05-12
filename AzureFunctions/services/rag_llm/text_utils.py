"""
Module docstring
"""
import re

def clean_text(text: str) -> str:
    """
    Normalise chunk text by:
     1. Removing PDF line-breaks (replace \n with space)
     2. Un-hyphenating words split across lines (remove “- ” at line ends)
     3. Collapsing any multi-space runs into one space
     4. Trimming leading/trailing whitespace
    """
    # 1) remove hard line-breaks
    t = text.replace("\n", " ")
    # 2) un-hyphenate line-end splits
    t = re.sub(r"-\s+", "", t)
    # 3) collapse any runs of whitespace
    t = re.sub(r"\s+", " ", t)
    return t.strip()
