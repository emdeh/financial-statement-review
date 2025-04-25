"""
services/rag_llm/embedding_service.py
Module docstring.
"""

from azure.search.documents import SearchClient
from azure.ai.openai import OpenAIClient
from services.chunk_service import ChunkService
from azure.identity import DefaultAzureCredential
import os
from services.logger import Logger

class EmbeddingService:
    """
    Class docstring.
    """
    def __init__(self):
        """
        Initialises the embedding service.
        """
        # Initialise the JSON logger for this service
        self.logger = Logger.get_logger("EmbeddingService", json_format=True)

        self.oaiclient = OpenAIClient(
            os.environ.get("AZURE_OPENAI_ENDPOINT"),
            credential=DefaultAzureCredential()
            )
        self.search_client = SearchClient(
            os.environ.get("SEARCH_ENDPOINT"),
            index_name=os.getenv("SEARCH_INDEX"),
            credential=DefaultAzureCredential()
        )

