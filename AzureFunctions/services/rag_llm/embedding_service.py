"""
services/rag_llm/embedding_service.py
Module docstring.
"""

import os
import datetime
from openai import AzureOpenAI, OpenAIError
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential
from services.logger import Logger
from services.rag_llm.chunk_service import ChunkService

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

        # Set up the Azure Search client
        self.search_client = SearchClient(
            endpoint=os.environ["SEARCH_ENDPOINT"],
            index_name=os.environ["SEARCH_INDEX"],
            credential=DefaultAzureCredential()
            )

        # Set up the OpenAI client
        self.oaiclient = AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            # TODO: Make this the same as the version deployed.
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
        )

        # Bind embedding deployment so the model doesn't need to be specified in each call
        self.oaiclient.deployment_name = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT_ID"]

        self.logger.info("Initialied AzureOpenAI & SearchClient")

    def index_chunks(self, document_name: str, ocr_pages: dict[int, str]):
        """
        Docstring
        """
        for page, text in ocr_pages.items():
            for chunk in ChunkService.chunk_text(text, page):
                try:
                    resp = self.oaiclient.embeddings.create(
                        model=self.oaiclient.deployment_name,
                        input=[chunk["text"]]
                    )
                    emb = resp.data[0].embedding

                    self.search_client.upload_documents([{
                        "id":            chunk["id"],
                        "documentName":  document_name,
                        "page":          chunk["page"],
                        "chunkText":     chunk["text"],
                        "embedding":     emb,
                        "createdAt":     datetime.datetime.utcnow().isoformat(),
                    }])
                except OpenAIError as oai_err:
                    self.logger.error("Embedding call failed: %s", str(oai_err),
                                      extra={"chunk_id": chunk["id"], "page": page})
                except Exception as e:
                    self.logger.error("Failed to index chunk to Search: %s", str(e),
                                      extra={"chunk_id": chunk["id"], "page": page})

# TODO: Consider collecting, batching chunks and then calling
# `upload_documents` to reduce API calls.
