"""
services/rag_llm/embedding_service.py
Module docstring.
"""

import os
import datetime
from openai import AzureOpenAI, OpenAIError
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
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
            credential=AzureKeyCredential(os.environ["SEARCH_ADMIN_KEY"]),
            api_version="2024-07-01"
            )

        # Set up the OpenAI client
        self.oaiclient = AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
        )

        # Bind embedding deployment so the model doesn't need to be specified in each call
        self.oaiclient.deployment_name = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]

        self.logger.info("Initialised AzureOpenAI & SearchClient")

    def index_chunks(self, document_name: str, page_texts: dict[int, str]):
        """
        Indexes each page’s text (embedded or OCR) into the Cognitive Search vector index,
        batching embeddings in a single API call for efficiency.
        """
        # 1) Build a flat list of all chunks
        all_chunks = []
        for page, text in page_texts.items():
            all_chunks.extend(ChunkService.chunk_text(text, page))

        if not all_chunks:
            return  # nothing to do

        try:
            # 2) Batch-embed them in one call
            texts = [c["text"] for c in all_chunks]
            resp = self.oaiclient.embeddings.create(
                model=self.oaiclient.deployment_name,
                input=texts
            )
            embeddings = [d.embedding for d in resp.data]

            # 3) Prepare Search documents
            docs = []
            for chunk, emb in zip(all_chunks, embeddings):
                docs.append({
                    "id":           chunk["id"],
                    "documentName": document_name,
                    "page":         chunk["page"],
                    "chunkText":    chunk["text"],
                    "embedding":    emb,
                    "createdAt":    datetime.datetime.utcnow().isoformat(),
                })

            # 4) Bulk upload to Azure Search
            self.search_client.upload_documents(docs)

        except OpenAIError as oai_err:
            # Log at the batch level
            self.logger.error(
                "Batch embedding call failed: %s", str(oai_err),
                extra={"document": document_name, "chunk_count": len(all_chunks)}
            )
        except Exception as e:
            # Catch any upload errors
            self.logger.error(
                "Failed to index chunks to Search: %s", str(e),
                extra={"document": document_name}
            )