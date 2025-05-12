"""
services/rag_llm/retrieval_service.py
Module for retrieval service to interact with Azure Search and OpenAI.

This module provides a service class to handle retrieval operations
using Azure Search and OpenAI. It includes methods to retrieve
text chunks based on a query, ask the OpenAI chat deployment
for answers with citations, and manage the Azure Search client.

Classes:
--------
    RetrievalService: A service class to handle retrieval operations
                      using Azure Search and OpenAI.
"""

import re
import os
import tiktoken
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from openai import AzureOpenAI, OpenAIError
from services.logger import Logger
from services.rag_llm.prompts import DEFAULT_SYSTEM_PROMPT
from services.rag_llm.text_utils import clean_text

class RetrievalService:
    """
    RetrievalService class to handle retrieval operations
    using Azure Search and OpenAI.

    Attributes
    ----------
        logger (Logger): Logger instance for logging messages.
        search_client (SearchClient): Azure Search client instance for querying documents.
        oaiclient (AzureOpenAI): Azure OpenAI client instance for generating embeddings and chat completions.
        system_prompt (str): The default system prompt for the OpenAI chat deployment.
        deoployment_name (str): The name of the OpenAI deployment for chat completions.

    Methods
    -------
        __init__(): Initialises the retrieval service with the necessary configuration.
        retrieve_chunks(): Retrieves the top k chunks from the search index based on the query.
        ask_with_citations(): Retrieves top-k chunks for a document matching a query,
                             then asks the OpenAI chat deployment to answer YES/NO + cite pages.

    """
    def __init__(self):
        """
        Initialises the retrieval service with the necessary configuration.
        Sets up the Azure Search client and OpenAI client using environment variables.

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

        enc = tiktoken.encoding_for_model(
            os.environ["AZURE_OPENAI_CHAT_MODEL"]
        )
        self._bias_yes = enc.encode(" yes")[0]
        self._bias_no  = enc.encode(" no")[0]

        # Set the default system prompt
        # Can override in env var deployment if needed.
        self.system_prompt = os.getenv("LLM_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

        self.logger.info("Initialised AzureOpenAI & SearchClient")

    def retrieve_chunks(self, document_name: str, query: str, k: int = 5, scoring_profile: str = None, scoring_parameters: list = None):
        """
        Retrieve the top k chunks from the search index based on the query.
        This method uses the Azure OpenAI client to generate an embedding for
        the query, then performs a vector search in the Azure Search index
        to find the most relevant chunks.

        Args:
            document_name (str): The name of the document to search in.
            query (str): The query string to search for (this is a 100% semantic
                    vector search, not a keyword search).

            k (int): The number of top results to retrieve. Default is 3.

        Returns:
            list: A list of dictionaries containing the top k chunks
                  with their IDs, page numbers, and text content.

        Raises:
            OpenAIError: If the embedding generation fails.
            AzureError: If the vector search fails.
        """

        # 1) Embed the user query
        # `query` here is a semantic vector search, not a keyword search.
        # `query` is defined in the checks.py file in the CHECKS list.
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
                top=k,
                scoring_profile=scoring_profile,
                scoring_parameters=scoring_parameters,
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
                        system_prompt: str = None,
                        scoring_profile: str = None,
                        scoring_parameters: list[str] = None,
                        filter_patterns: list[str] = None,
                        include_patterns: list[str] = None
                    ) -> dict:
        """
        Retrieve top-k chunks for `document_name` matching `query`, then
        ask the AzureOpenAI chat deployment to answer YES/NO + cite pages.
        """
        # 1) retrieve relevant chunks
        chunks = self.retrieve_chunks(
            document_name,
            query,
            k,
            scoring_profile,
            scoring_parameters
            )
        
        if filter_patterns or include_patterns:
            def keep(chunk):
                raw = chunk["text"]
                text = clean_text(raw)

                # If it matches any include_pattern, always keep it
                if include_patterns and any(re.search(p, text, re.IGNORECASE)
                                            for p in include_patterns):
                    return True

                # If it matches any filter_pattern, discard it
                if filter_patterns and any(re.search(p, text, re.IGNORECASE)
                                            for p in filter_patterns):
                    return False

                # Otherwise, keep it
                return True
            chunks = [c for c in chunks if keep(c)]
        
        # DEBUG: Inspect each chunk's context
        for c in chunks:
            print("DEBUG - CHUNKS INCLUDED IN PROMPT")
            print(f"DEBUG ─ CHUNK ID={c['id']}, page={c['page']}, tokens≈{len(c['text'].split())}")
            print(f"DEBUG ─ TEXT SNIPPET: {c['text'][:200]!r}\n")
        
        # print(f"DEBUG - Retrieved {len(chunks)} chunks for query '{query}'")

        # 2) build the prompt with inline citations
        lines = [
            f"QUESTION: {question}",
            "Use the following excerpts to answer:",
            ]

        for c in chunks:
            lines.append(f"- (Page {c['page']}) {c['text']}")

        lines.extend([
            "",
            "Answer **YES** or **NO** only.",
            "If YES, provide citations exactly like this: CITATIONS: [12, 34]."
        ])
        user_prompt = "\n".join(lines)
        # print(f"DEBUG - USER prompt: {user_prompt}")

        # 3) Choose which system message to use
        sys_msg = system_prompt or self.system_prompt
        # print(f"DEBUG - SYSTEM prompt: {sys_msg}")

        # 4) call the chat completion endpoint
        try:
            chat_resp = self.oaiclient.chat.completions.create(
                model=self.oaiclient.deployment_name,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user",   "content": user_prompt}
                ],
                temperature=0.0,
                top_p=0,
                max_tokens=10,
                logit_bias={
                    str(self._bias_yes): 50,
                    str(self._bias_no):  50
                },
            )
            answer = chat_resp.choices[0].message.content.strip()
            # print(f"DEBUG - chat_resp: {chat_resp}")
            # print(f" DEBUG - Chat response: {answer}")

        except OpenAIError as err:
            self.logger.error(
                "Chat completion failed: %s", str(err),
                extra={"check": check_name}
            )
            answer = "NO — (error)"

        # 5) parse out any cited page numbers in either bracket or “page X” form
        bracketed = re.findall(r"\[([0-9,\s]+)\]", answer)
        if bracketed:
            parsed = [int(n) for part in bracketed for n in part.split(",")]
        else:
            parsed = [int(p) for p in re.findall(r"page\s*(\d+)", answer, flags=re.IGNORECASE)]

        # 6) only fallback on YES if still empty
        if answer.upper().startswith("YES") and not parsed:
            parsed = [c["page"] for c in chunks]

        citations = sorted(set(parsed))

        return {"answer": answer, "citations": citations}

