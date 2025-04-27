"""
services/rag_llm/retrieval_service.py
Module docstring.
"""

import re
import os
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorQuery
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI, OpenAIError
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
        # Set up the OpenAI client
        self.oaiclient = AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
        )

        # Bind chat deployment so the model doesn't need to be specified in each call
        self.chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_ID")
        self.oaiclient.deployment_name = self.chat_deployment

    def retrieve_chunks(self, document_name: str, query: str, k: int = 3):
        """
        Retrieves the top k chunks from the search index based on the query.
        """
        # 1) embed query
        resp = self.oaiclient.embeddings.create(
            model=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
            input=[query]
        )
        qemb = resp.data[0].embedding

        # 2) Vector search WITH filter on documentName
        results = self.search.search(
            search_text="*", # ignored when vector present
            vector=VectorQuery(vector=qemb, k=k, fields=["embedding"]),
            filter=f"documentName eq '{document_name}'",
            select=["id","page","chunkText"]
        )
        return [{"id": r["id"], "page": r["page"], "text": r["chunkText"]} for r in results]

    def ask_with_citations(self,
                        document_name: str,
                        check_name: str,
                        question: str,
                        query: str):
        """
        Retrieve top-k chunks for `document_name` matching `query`, then
        ask the AzureOpenAI chat deployment to answer YES/NO + cite pages.
        """
        # 1) retrieve relevant chunks
        chunks = self.retrieve_chunks(document_name, query)

        # 2) build the prompt with inline citations
        prompt = f"QUESTION: {question}\n\n"
        for c in chunks:
            prompt += f"[Page {c['page']} | Chunk {c['id']}]\n{c['text']}\n\n"
        prompt += "Answer YES or NO. If YES, list the page number(s). Answer:"

        # 3) call the chat completion endpoint
        try:
            chat_resp = self.oaiclient.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a precise assistant."},
                    {"role": "user",   "content": prompt}
                ]
            )
            answer = chat_resp.choices[0].message.content.strip()
        except OpenAIError as err:
            self.logger.error(
                "Chat completion failed: %s", str(err),
                extra={"check": check_name}
            )
            answer = "NO — (error)"

        # 4) parse out any cited page numbers
        pages = [
            int(p)
            for p in re.findall(r"page\s*(\d+)", answer, flags=re.IGNORECASE)
        ]

        return {"answer": answer, "citations": sorted(set(pages))}
