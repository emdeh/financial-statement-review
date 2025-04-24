"""
services/pdf_utils.py
Module docstring.
This module provides utility functions for working with PDF files.
"""

import io
from PyPDF2 import PdfReader
from services.logger import Logger

class PDFService:
    """
    A service class to handle PDF operations.
    
    This class provides methods to extract text from PDF files, both digitally generated and scanned.
    
    Methods:
        extract_embedded_text(pdf_bytes: bytes) -> str:
            Attempts to extract text directly from a digitally generated PDF using PyPDF2.
    """

    def __init__(self):
        """
        Initialises the PDF service.
        """
        # Initialise the JSON logger for this service
        self.logger = Logger.get_logger("PDFService", json_format=True)

    def is_pdf(self, pdf_bytes: bytes) -> bool:
        """
        Checks if the provided bytes represent a PDF file by looking for the %PDF- header.
        """
        return pdf_bytes.startswith(b"%PDF-")

    def extract_embedded_text(self, pdf_bytes: bytes) -> str:
        """
        Attempts to extract text directly from a digitally generated PDF using PyPDF2.
        
        Args:
            pdf_bytes (bytes): PDF file content.
        
        Returns:
            str: Extracted text. May be empty if the PDF is scanned.
        """
        text = ""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            # Log the error with the exception message
            self.logger.error("Error extracting text from PDF: %s, falling back to OCR", str(e))
            # In case of any error, return empty string to fallback to OCR.
            text = ""
        return text.strip()
