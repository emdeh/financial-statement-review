"""
services/pdf_utils.py
Module for PDF utilities.

This module provides a service class to handle PDF operations, including
extracting text from PDF files. It includes methods to extract text from
digitally generated PDFs and to check if the provided bytes represent
a PDF file.

Classes:
--------
    PDFService: A service class to handle PDF operations.
"""

import io
import re
from typing import Dict
from PyPDF2 import PdfReader
from services.logger import Logger

class PDFService:
    """
    A service class to handle PDF operations.
    This class includes methods to extract text from digitally generated
    PDFs and to check if the provided bytes represent a PDF file.

    Attributes
    ----------
        logger (Logger): Logger instance for logging messages.

    Methods
    -------
        __init__() Initialises the PDF service.
        is_pdf(): Checks if the provided bytes represent a PDF file.
        extract_embedded_text(): Extracts text from a digitally generated PDF 
        using PyPDF2.
        get_page_count(): Returns the number of pages in the PDF.
        find_abn(): Searches the extracted text for an Australian Business 
        Number (ABN).

    """

    def __init__(self):
        """
        Initialises the PDF service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        # Initialise the JSON logger for this service
        self.logger = Logger.get_logger("PDFService", json_format=True)

    def is_pdf(self, pdf_bytes: bytes) -> bool:
        """
        Checks if the provided bytes represent a PDF file.

        Args:
            pdf_bytes (bytes): PDF file content.

        Returns:
            bool: True if the bytes represent a PDF file, False otherwise.

        Raises:
            None
        """
        return pdf_bytes.startswith(b"%PDF-")

    def extract_embedded_text(self, pdf_bytes: bytes) -> Dict[int, str]:
        """
        Extracts text from a digitally generated PDF using PyPDF2.

        Args:
            pdf_bytes (bytes): PDF file content.

        Returns:
            Dict[int, str]: A dictionary where keys are page numbers and values
            are the extracted text from each page.

        Raises:
            Exception: If there is an error extracting text from the PDF.
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
        Returns the number of pages in the PDF.

        Args:
            pdf_bytes (bytes): PDF file content.

        Returns:
            int | None: The number of pages in the PDF, or None if an error occurs.

        Raises:
            Exception: If there is an error counting the pages in the PDF.
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
        Searches the extracted text for an Australian Business Number (ABN).

        Args:
            text (str): The text extracted from the PDF.

        Returns:
            str | None: The ABN if found, or None if not found.

        Raises:
            None
        """
        # Look for patterns like "12 345 678 901" or "12345678901"
        match = re.search(r"\b(\d{2}\s?\d{3}\s?\d{3}\s?\d{3})\b", text)
        if not match:
            return None

        # Normalise by stripping out any spaces
        abn = re.sub(r"\s+", "", match.group(1))
        self.logger.info("PDFService.find_abn", extra={"abn": abn})
        return abn
