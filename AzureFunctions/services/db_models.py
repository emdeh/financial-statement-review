"""
    services/db_models.py
    Module for database models used in the Azure Functions project.

    This module defines the data models used for storing and retrieving
    document processing results in Azure Cosmos DB. It includes the
    DocumentResult model, which represents the result of a document
    processing operation.

    Classes:
    ---------
        DocumentResult: A Pydantic model representing the result of a document
                        processing operation.

    Notes
    -----
        - Field names follow **camelCase** to align with the wider JSON contract,
            but Pydantic aliases (e.g. `afsConfidence`) ensure external consumers
            see the expected casing.
        - Set `allow_population_by_field_name = True` so callers can provide either
            the original attribute name or its alias.
        - Extend `DocumentResult` if additional checks are added to `CheckDef`.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class DocumentResult(BaseModel):
    """
    DocumentResult model to represent the result of a document processing operation.
    
    This model includes various attributes related to the document, such as its ID,
    name, page count, extraction method, LLM+RAG checks, and validation status.

    Attributes
    ----------
        - As described below.

    Methods
    -------
        - Nil

    Example
    -------
        >>> doc_result = DocumentResult(
                id="12345",
                documentName="example.pdf",
                isPDF=True,
                pageCount=10,
                blobUrl="https://example.com/blob",
                extractionMethod="embedded-text",
                isValidAFS=True,
                afsConfidence=0.95,
                hasABN=True,
                ABN="123456789",
                hasProfitLoss=True,
                profitLossPages=[1, 2],
                hasBalanceSheet=False,
                balanceSheetPages=[],
                hasCashFlow=True,
                cashFlowPages=[3],
                timestamp=datetime.now()
            )
  
    Notes
    -----
        - The model should include the names from CheckDef in checks.py.

    See Also
    --------
        - CheckDef : Class to define the checks for the document processing.
        - pydantic.BaseModel : Base class for creating Pydantic models.     
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
    hasProfitLoss: Optional[bool] = None
    profitLossPages: Optional[list[int]] = None
    hasBalanceSheet: Optional[bool] = None
    balanceSheetPages: Optional[list[int]] = None
    hasCashFlow: Optional[bool] = None
    cashFlowPages: Optional[list[int]] = None
    hasGoingConcern: Optional[bool] = None
    goingConcernPages: Optional[list[int]] = None
    timestamp: datetime

    class Config:
        """
        Pydantic model configuration.
        This configuration allows the model to be populated by field names
        """
        allow_population_by_field_name = True
