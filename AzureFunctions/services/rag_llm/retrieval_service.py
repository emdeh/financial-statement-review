"""
services/rag_llm/retrieval_service.py
Module docstring.
"""

import re
import os
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from openai import AzureOpenAI, OpenAIError
from services.logger import Logger
from services.rag_llm.prompts import DEFAULT_SYSTEM_PROMPT

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

        # Bind chat deployment so the model doesn't need to be specified in each call
        self.oaiclient.deployment_name = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]

        # Set the default system prompt
        # Can override in env var deployment if needed.
        self.system_prompt = os.getenv("LLM_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

        self.logger.info("Initialised AzureOpenAI & SearchClient")

    def retrieve_chunks(self, document_name: str, query: str, k: int = 3):
        """
        Retrieves the top k chunks from the search index based on the query.
        """

        # 1) Embed the user query
        try:
            resp = self.oaiclient.embeddings.create(
                model=os.environ["AZURE_OPENAI_EMBEDDING_MODEL"],
                input=[query]
            )
            qemb = resp.data[0].embedding

        except OpenAIError as err:
            self.logger.error(
                "Embedding call failed: %s", str(err),
                extra={"document": document_name, "query": query}
            )
            return []

        # 2) build the vector query
        vquery = VectorizedQuery(
            vector=qemb,
            fields="embedding",
            k_nearest_neighbors=k,
            kind="vector",
        )

        # 3) Prepare the documentName filter
        escaped = document_name.replace("'", "''")
        odata_filter = f"documentName eq '{escaped}'"

        # 4) Execute filtered vector search
        try:
            paged = self.search_client.search(

            # `paged` is an instance of the Azure Search SDK’s ItemPaged
            # (aka SearchPaged) class.
            # It lazily pages through results in batches on demand and can only
            # be consumed once.
            #
            # • Lazy paging: it fetches the first batch of results only when you
            # start iterating, then fetches subsequent batches as you consume them.
            #
            # • Single-use iterator: once you’ve walked through all batches,
            # even just one page, the iterator is exhausted and cannot be
            # rewound or reused.

                search_text="*",  # wildcard so lexical filter is bypassed
                vector_queries=[vquery],
                filter=odata_filter,
                select=["id", "page", "chunkText"],
                timeout=20,
                top=k
            )

            # Very important to "materialise" the SearchPaged iterator into a list.
            # Converting to list forces all batches to be fetched and stores
            # them in memory, allowing multiple passes for logging, debugging,
            # and return without re-fetching.
            #
            # I hope this comment helps avoid some heartache for future readers.
            # The one who plants trees, knowing that he will never sit in their
            # shade, has at least started to understand the meaning of life...

            results = list(paged) # For the love of God, materialise this iterator!
            self.logger.info(
                "Retrieved %d chunk(s) for '%s'", 
            len(results), document_name
        )

        except AzureError as err:
            self.logger.error(
                "Vector search failed: %s", str(err),
                extra={"document": document_name, "query": query}
            )
            return []

        # 5) (Optional) Debug each hit
        """
        for hit in results:
            # DEBUG: log the raw hits
            self.logger.debug(
                "Retrieved chunk",
                extra={
                    "chunk_id":   hit["id"],
                    "page":       hit["page"],
                    "text_snip":  hit["chunkText"][:200]  # first 200 chars
                }
            )
        """
        # 6) Return minimal info
        return [
            {"id": r["id"], "page": r["page"], "text": r["chunkText"]}
            for r in results
        ]

    def ask_with_citations(self,
                        document_name: str,
                        check_name: str,
                        question: str,
                        query: str,
                        k: int = 3,
                        system_prompt: str = None
                    ):
        """
        Retrieve top-k chunks for `document_name` matching `query`, then
        ask the AzureOpenAI chat deployment to answer YES/NO + cite pages.
        """
        # 1) retrieve relevant chunks
        chunks = self.retrieve_chunks(document_name, query, k)
        # print(f"DEBUG - Retrieved {len(chunks)} chunks for query '{query}'")

        # 2) build the prompt with inline citations
        user_prompt = f"QUESTION: {question}\n\n"
        for c in chunks:
            #print(c["text"])
            user_prompt += f"[Page {c['page']} | Chunk {c['id']}]\n{c['text']}\n\n"
        user_prompt += "Answer YES or NO. If YES, list the page number(s). Answer:"
        print(f"DEBUG - {user_prompt}")

        # 3) Choose which system message to use
        sys_msg = system_prompt or self.system_prompt
        print(f"DEBUG - Using system prompt: {sys_msg}")


        # 4) call the chat completion endpoint
        try:
            chat_resp = self.oaiclient.chat.completions.create(
                model=self.oaiclient.deployment_name,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user",   "content": user_prompt}
                ]
            )
            answer = chat_resp.choices[0].message.content.strip()
            print(f" DEBUG - Chat response: {answer}")

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

