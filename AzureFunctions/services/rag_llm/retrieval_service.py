"""
services/rag_llm/retrieval_service.py
Module docstring.
"""

import re
import os
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from services.logger import Logger

class RetrievalService:
    """
    Class docstring.
    """
    def __init__(self):
        """
        Initialises the retrieval service.
        """
        # Initialise the JSON logger for this service
        self.logger = Logger.get_logger("RetrievalService", json_format=True)

        self.search = SearchClient(endpoint=os.environ.get("SEARCH_ENDPOINT"),
                                   index_name=os.environ.get("SEARCH_INDEX"),
                                   credential=DefaultAzureCredential()
                                   )
        self.oaiclient = AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
        )

    def retrieve_chunks(self, document_name: str, query: str, k: int = 3):
        """
        Retrieves the top k chunks from the search index based on the query.
        """
        # 1) embed query
        qemb = self.oaiclient.get_embeddings(
            model=os.environ.get("EMBEDDING_MODEL"),
            input=[query]
        ).data[0].embedding

        # 2) Vector search WITH filter on documentName
        results = self.search.search(
            search_text="*", # ignored when vector present
            vector=VectorQuery(vector=qemb, k=k, fields=["embedding"]),
            filter=f"documentName eq '{document_name}'",
            select=["id","page","chunkText"]
        )
        return [{"id": r["id"], "page": r["page"], "text": r["chunkText"]} for r in results]

    def ask_with_citations(self, document_name: str,
                           check_name: str, question: str, query: str):
        # retrieve
        chunks = self.retrieve_chunks(document_name, query)
        # build prompt with inline citations
        prompt = f"QUESTION: {question}\n\n"
        for c in chunks:
            prompt += f"[Page {c['page']} | Chunk {c['id']}]\n{c['text']}\n\n"
        prompt += "Answer YES or NO. If YES, list the page number(s). Answer:"

        # call ChatCompletion
        resp = self.oaiclient.get_chat_completions(
            engine=os.getenv("OPENAI_DEPLOYMENT"),
            messages=[
              {"role":"system","content":"You are a precise assistant."},
              {"role":"user","content":prompt}
            ]
        ).choices[0].message.content.strip()

        # extract page citations
        pages = [int(p) for p in re.findall(r"page\s*(\d+)", resp, flags=re.IGNORECASE)]
        return {"answer": resp, "citations": sorted(set(pages))}