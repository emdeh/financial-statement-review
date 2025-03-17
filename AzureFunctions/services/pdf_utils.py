"""
services/pdf_utils.py
Module docstring.
This module provides utility functions for working with PDF files.
"""

import io
from PyPDF2 import PdfReader

def extract_embedded_text(pdf_bytes: bytes) -> str:
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
    except Exception:
        # In case of any error, return empty string to fallback to OCR.
        text = ""
    return text.strip()
