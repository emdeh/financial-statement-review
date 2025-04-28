"""
services/pdf_utils.py
Module docstring.
This module provides utility functions for working with PDF files.
"""

import io
import re
from typing import Dict
from PyPDF2 import PdfReader
from services.logger import Logger

class PDFService:
    """
    A service class to handle PDF operations.
    
    This class provides methods to extract text from PDF files, both digitally 
    generated and scanned.
    
    Methods:
        extract_embedded_text(pdf_bytes: bytes) -> str:
            Attempts to extract text directly from a digitally generated PDF 
            using PyPDF2.
    """

    def __init__(self):
        """
        Initialises the PDF service.
        """
        # Initialise the JSON logger for this service
        self.logger = Logger.get_logger("PDFService", json_format=True)

    def is_pdf(self, pdf_bytes: bytes) -> bool:
        """
        Checks if the provided bytes represent a PDF file by looking 
        for the %PDF- header.
        """
        return pdf_bytes.startswith(b"%PDF-")

    def extract_embedded_text(self, pdf_bytes: bytes) -> Dict[int, str]:
        """
        Attempts to extract text directly from a digitally generated PDF 
        using PyPDF2.
        
        Args:
            pdf_bytes (bytes): PDF file content.
        
        RReturns:
            Dict[int,str]: Mapping of page number → extracted text
                           (empty string if no text on that page).
        """
        page_texts: Dict[int, str] = {}
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for idx, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                page_texts[idx] = text

        except Exception as e:
            Logger.get_logger("PDFService").error(
                "Error extracting embedded text: %s – falling back to OCR", str(e)
            )
            # return an empty dict so main.py knows to OCR instead
            return {}
        return page_texts

    def get_page_count(self, pdf_bytes: bytes) -> int | None:
        """
        Returns the number of pages in the PDF, or None if it can't be read.
        """
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            count = len(reader.pages)
            self.logger.info("PDFService.get_page_count", extra={"pageCount": count})
            return count
        except Exception as e:
            self.logger.error("Error counting PDF pages: %s", str(e))
            return None

    def find_abn(self, text: str) -> str | None:
        """
        Search the extracted text for an Australian Business Number (ABN).
        Returns the 11-digit ABN (no spaces) if found, else None.
        """
        # Look for patterns like "12 345 678 901" or "12345678901"
        match = re.search(r"\b(\d{2}\s?\d{3}\s?\d{3}\s?\d{3})\b", text)
        if not match:
            return None

        # Normalise by stripping out any spaces
        abn = re.sub(r"\s+", "", match.group(1))
        self.logger.info("PDFService.find_abn", extra={"abn": abn})
        return abn
