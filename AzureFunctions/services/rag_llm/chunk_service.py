"""
services/rag_llm/chunk_service.py
Module for chunking text into smaller segments.

This module provides a service class to handle chunking text
into smaller segments for processing. It includes methods to
split the text into chunks of a specified size with overlap,
and to handle the metadata associated with each chunk.

Classes:
--------
    DynamicChunker: A service class to handle text chunking operations.

Module-level constants:
    BLANK_LINE_RE: Regex to match blank lines.
    SHORT_CAPS_RE: Regex to match short all-caps lines.
"""

import os
import re
from typing import List, Dict

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Module-level constants
BLANK_LINE_RE  = re.compile(r"\n\s*\n")          # paragraph gap
SHORT_CAPS_RE  = re.compile(r"^\s*[A-Z &]{6,}$") # centred ALL‑CAPS line

class DynamicChunker:
    """
    Split PDF-extracted text into ~300-token chunks with adaptive overlap.

    Environment variables:
        Defined in local.settings.json
            CHUNK_TOKENS:  Max tokens per chunk (default: 300).
            CHUNK_OVERLAP: Fractional overlap (0-1). Default: 0.1  (10 % of CHUNK_TOKENS)
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