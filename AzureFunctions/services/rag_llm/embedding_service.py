"""
services/rag_llm/embedding_service.py
Module for embedding service to index text chunks into Azure Cognitive Search.

This module provides a service class to handle the embedding of text
chunks into Azure Cognitive Search. It includes methods to index
text chunks, handle embedding errors, and manage the Azure Search
client. The service class retrieves the necessary configuration
parameters from environment variables and implements a robust
embedding process that batches the text chunks for efficient
processing. The class also includes error handling for various
scenarios, including request failures and indexing errors.

Classes:
--------
    EmbeddingService: A service class to handle embedding operations
                      using Azure OpenAI and Azure Cognitive Search.
"""

import os
import datetime
from openai import AzureOpenAI, OpenAIError
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from services.logger import Logger
from services.rag_llm.chunk_service import DynamicChunker

class EmbeddingService:
    """
    A service class to handle embedding operations using Azure OpenAI
    and Azure Cognitive Search. This class includes methods to index
    text chunks into the search index, handle embedding errors, and
    manage the Azure Search client. The service class retrieves the
    necessary configuration parameters from environment variables and
    implements a robust embedding process that batches the text chunks
    for efficient processing. The class also includes error handling
    for various scenarios, including request failures and indexing errors.
    The embedding process is designed to ensure that the text chunks
    are indexed correctly and efficiently, allowing for fast retrieval
    and search capabilities in the Azure Cognitive Search index.

    Attributes
    ----------
        logger (Logger): Logger instance for logging messages.
        batch_size (int): The number of text chunks to process in each batch.
        search_client (SearchClient): Azure Search client instance for indexing documents.
        oaiclient (AzureOpenAI): Azure OpenAI client instance for generating embeddings.
        deployment_name (str): The name of the OpenAI deployment for embeddings.
        chunker (DynamicChunker): Instance of the DynamicChunker class for chunking text.
    
    Methods
    -------
        __init__(): Initialises the embedding service with the necessary configuration.
        index_chunks(): Indexes each page's text (embedded or OCR) into the 
                        Cognitive Search vector index, batching embeddings
                        in a single API call for efficiency.
    """
    def __init__(self):
        """
        Initialises the embedding service with the necessary configuration.
        """
        # Initialise the JSON logger for this service
        self.logger = Logger.get_logger("EmbeddingService", json_format=True)

        self.batch_size = int(os.environ.get("BATCH_SIZE", 20))
        self.logger.info("Using embedding batch size %s", self.batch_size)

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

        # Create a reusable chunker instance
        self.chunker = DynamicChunker()

        self.logger.info("Initialised AzureOpenAI & SearchClient")

    def index_chunks(self, document_name: str, page_texts: dict[int, str]):
        """
        Indexes each page's text (embedded or OCR) into the Cognitive Search
        vector index, batching embeddings in a single API call for efficiency.

        Args:
            document_name (str): The name of the document being processed.
            page_texts (dict[int, str]): A dictionary where keys are page numbers
                                         and values are the extracted text from each page.

        Returns:
            None

        Raises:
            OpenAIError: If there is an error with the OpenAI API call.
            Exception: If there is an error with the Azure Search client.
        """
        # 1) Build a flat list of all chunks
        #chunks = []
        #for page, text in page_texts.items():
        #    chunks.extend(ChunkService.chunk_text(text, page))
        chunker = self.chunker
        chunks: list[dict] = []
        for page, text in page_texts.items():
            chunks.extend(chunker.chunk_page(text, page))

        # 2) Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            texts = [c["text"] for c in batch]

            # 3) Embed + prepare docs
            try:
                resp = self.oaiclient.embeddings.create(
                    model=self.oaiclient.deployment_name,
                    input=texts
                )
                embeddings_list = [d.embedding for d in resp.data]

                # 3) Prepare Search documents
                docs = []
                for c, emb in zip(batch, embeddings_list):
                    docs.append({
                        "id":           c["id"],
                        "documentName": document_name,
                        "page":         c["page"],
                        "tokens":       c["tokens"],
                        "chunkText":    c["text"],
                        "embedding":    emb,
                        "createdAt":    datetime.datetime.utcnow().isoformat(),
                    })

                # 4) Upload and log each result
                self.search_client.upload_documents(docs)
                self.logger.info(
                    "Indexed chunks %s - %s",
                    batch[0]["id"], batch[-1]["id"],
                    extra={"batchSize": len(batch), "document": document_name}
                )


            except OpenAIError as oai_err:
                # Log at the batch level
                self.logger.error(
                    "Batch embedding call failed: %s", str(oai_err),
                    extra={"document": document_name, "chunk_count": len(chunks)}
                )
            except Exception as e:
                # Catch any upload errors
                self.logger.error(
                    "Failed to index chunks to Search: %s", str(e),
                    extra={"document": document_name}
                )
