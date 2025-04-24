"""
Relative location: ProcessPDF/services/db_models.py
Module for database models used in the Azure Function.
This module defines the DocumentResult model, which represents the result of a 
document processing operation.
This model includes various attributes related to the document, such as its ID, name, page count,
extraction method, and validation status.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class DocumentResult(BaseModel):
    """
    DocumentResult model to represent the result of a document processing operation.
    This model includes various attributes related to the document, such as its ID,
    name, page count, extraction method, and validation status.     
    """
    id: str
    documentName: str
    isPDF: bool
    pageCount: Optional[int] = None
    blobUrl: str
    extractionMethod: Optional[str] = None
    isValidAFS: Optional[bool] = None
    afsConfidence: Optional[float] = Field(None, alias="afsConfidence")
    hasABN: Optional[bool] = None
    ABN: Optional[str] = None
    timestamp: datetime

    class Config:
        """
        Pydantic model configuration.
        This configuration allows the model to be populated by field names
        """
        allow_population_by_field_name = True
