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
