"""
services/rag_llm/chunk_service.py
Module docstring.
"""

class ChunkService:
    """
    Class docstring.
    """
    CHUNK_SIZE = 1000 # max chars per chunk
    OVERLAP = 200 # chars to overlap

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
            snippet = text[start : end]
            chunk_id = f"{page}__{start}"
            chunks.append({"id": chunk_id, "page": page, "text": snippet})

            # 4) Advance, perserving the overlap
            start = end - ChunkService.OVERLAP

        return chunks
