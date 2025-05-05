"""
services/rag_llm/chunk_service.py
Module for chunking text into smaller segments.

This module provides a service class to handle chunking text
into smaller segments for processing. It includes methods to
split the text into chunks of a specified size with overlap,
and to handle the metadata associated with each chunk.

Classes:
--------
    ChunkService: A service class to handle text chunking operations.
"""

import os
import re
from typing import List, Dict

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

BLANK_LINE_RE  = re.compile(r"\n\s*\n")          # paragraph gap
SHORT_CAPS_RE  = re.compile(r"^\s*[A-Z &]{6,}$") # centred ALL‑CAPS line

class ChunkService:
    """
    A service class to handle text chunking operations.
    This class includes methods to split the text into smaller
    segments for processing. It allows for chunking text into
    smaller segments of a specified size with overlap, and
    handles the metadata associated with each chunk.
    The chunking process is designed to ensure that the text
    is split at appropriate boundaries, such as whitespace,
    to avoid breaking words or sentences in the middle.

    Attributes
    ----------
        CHUNK_SIZE (int): The maximum number of characters per chunk.
        OVERLAP (int): The number of characters to overlap between chunks.
    
    Methods
    -------
        chunk_text(): Splits the text into chunks of a specified size with overlap.

    """
    CHUNK_SIZE = 500 # max chars per chunk
    OVERLAP = 100 # chars to overlap

    @staticmethod
    def chunk_text(text: str, page: int) -> list[dict]:
        """
        Splits the text into chunks of a specified size with overlap.

        Args:
            text (str): The text to be chunked.
            page (int): The page number from which the text was extracted.

        Returns:
            list[dict]: A list of dictionaries containing the chunked text and its metadata.

        Raises:
            ValueError: If the text is empty or if the page number is invalid.
    
        """
        chunks = []
        start = 0
        seen = set()
        length = len(text)

        while start < length:

            #1 ) Pick up tentative end position
            end = min(start + ChunkService.CHUNK_SIZE, length)

            # 2) If not at the very end, back up to the last whitespace
            if end < length:
                last_space = text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space

            # 3) Extract the snippet
            snippet = text[start:end].strip()
            # print(f"Chunking text: {snippet}")
            chunk_id = f"{page}__{start}"
            chunks.append({"id": chunk_id, "page": page, "text": snippet})

            # 4) compute next start with clamp
            next_start = max(end - ChunkService.OVERLAP, 0)
            # prevent infinite loop if no progress
            if next_start <= start or next_start in seen:
                break
            # skip leading whitespace
            while next_start < length and text[next_start].isspace():
                next_start += 1
            seen.add(start)
            start = next_start

        return chunks

class DynamicChunker:
    """
    Split PDF-extracted text into ~300-token chunks with adaptive overlap.

    Environment variables:
        CHUNK_TOKENS:  Max tokens per chunk (default: 300).
        CHUNK_OVERLAP: Fraction of overlap between chunks (default: 0.0).
        AZURE_OPENAI_EMBEDDING_MODEL: Model name for tokenization.

    Module variables:
        BLANK_LINE_RE: Regex to match blank lines.
        SHORT_CAPS_RE: Regex to match short all-caps lines.
    """
    
    def __init__(self) -> None:
        # Read settings with safe fall-backs
        self.chunk_tokens = int(os.environ.get("CHUNK_TOKENS", 300))
        overlap_frac = float(os.environ.get("CHUNK_OVERLAP", 0.1))
        self.model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL",
                               "text-embedding-3-small")

        # Initialise helpers
        self.enc = tiktoken.encoding_for_model(self.model)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size   = self.chunk_tokens,
            chunk_overlap= int(self.chunk_tokens * overlap_frac),
        )

    def _token_len(self, text: str) -> int:
        return len(self.enc.encode(text))

    def _page_blocks(self, text: str) -> List[str]:
        """First-pass block split by layout gaps or uppercase headings."""
        lines, blocks, buf = text.splitlines(), [], []
        for line in lines:
            if BLANK_LINE_RE.match(f"\n{line}\n") or SHORT_CAPS_RE.match(line):
                if buf:
                    blocks.append("\n".join(buf).strip())
                    buf = []
            buf.append(line)
        if buf:
            blocks.append("\n".join(buf).strip())
        return [b for b in blocks if b]  # drop empties

    def chunk_page(self, text: str, page: int) -> List[Dict]:
        """Return list of {id, page, text, tokens} ready for embedding."""
        chunks, cid = [], 0
        for block in self._page_blocks(text):
            for piece in self.splitter.split_text(block):
                chunks.append(
                    {
                        "id":     f"{page}_{cid}",
                        "page":   page,
                        "text":   piece,
                        "tokens": self._token_len(piece),
                    }
                )
                cid += 1
        return chunks