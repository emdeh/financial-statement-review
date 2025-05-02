"""
services/rag_llm/chunk_service.py
Module docstring.
"""

class ChunkService:
    """
    Class docstring.
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
