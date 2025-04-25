"""
services/rag_llm/chunk_service.py
Module docstring.
"""

class ChunkService:
    """
    Class docstring.
    """
    CHUNK_SIZE = 1000 # characters per chunk
    OVERLAP = 200 # overlap between chunks to preserve context

    @staticmethod
    def chunk_text(text: str, page: int) -> list[dict]:
        """
        Splits the text into chunks of a specified size with overlap.

        Args:
            text (str): The text to be chunked.
            page (int): The page number from which the text was extracted.

        Returns:
            list[dict]: A list of dictionaries containing the chunked text and its metadata.
        """
        chunks = []
        start = 0
        while start < len(text):
            snippet = text[start : start + ChunkService.CHUNK_SIZE]
            chunk_id = f"{page}__{start}"
            chunks.append({"id": chunk_id, "page": page, "text": snippet})
            start += ChunkService.CHUNK_SIZE - ChunkService.OVERLAP
        return chunks