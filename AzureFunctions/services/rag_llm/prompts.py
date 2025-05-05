"""
services/rag_llm/prompts.py
Module for defining system prompts for the LLM.

This module provides a set of system prompts to be used with
the LLM for various tasks. The prompts are designed to
provide clear instructions to the LLM, ensuring that it
understands the context and requirements of the task.

Attributes:
--------
    DEFAULT_SYSTEM_PROMPT (str): 
        The default system prompt to be used when no specific prompt is provided. 
        This prompt is designed to instruct the LLM to be precise and accurate 
        in its responses.
"""

DEFAULT_SYSTEM_PROMPT = (
    "You are a precise assistant."
)
