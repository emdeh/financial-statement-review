"""
    Relative location: ProcessPDF/main.py
    Main entry point for the Azure Function triggered by a blob upload.

    This function processes the uploaded blob, logs relevant information, and
    traces the operation using Application Insights.

    Args:
        myblob (func.InputStream): The input blob stream that triggered the function.
"""
import os
import azure.functions as func
from services.logger import Logger
from services.tracer import AppTracer

# Initialise the JSON logger for this function
logger = Logger.get_logger("ProcessPDF", json_format=True)

# Retrieve the Application Insights instrumentation key from an environment variable
instrumentation_key = os.environ.get(
    "APPINSIGHTS_INSTRUMENTATIONKEY",
    "your_instrumentation_key_here"
    )

# Initialise the tracer with the instrumentation key
tracer = AppTracer(instrumentation_key)

# Dummy simulation functions for OCR and ML model
def simulate_ocr(pdf_bytes):
    """
    Simulates OCR processing on a PDF document.
    """
    return "Extracted text from PDF. This is a simulated OCR output."

def simulate_ml_classification(text):
    """
    Simulates a machine learning classification model.
    """
    return {
        "is_valid_afs": True,
        "confidence": 0.95,
        "ml_message": "The document is valid and meets the AFS requirements."
    }

def simulate_write_to_db(result):
    """
    Simulates writing the classification result to a database.
    """
    return {"status:": "Success", "db_message": "Simulate write succssful."}

def main(myblob: func.InputStream):
    """
    Main entry point for the Azure Function.
    """
    with tracer.span(name="ProcessPDFOperation") as span:
        # Log the beginning of the blob processing operation, including extra context.
        logger.info("Blob trigger function processed blob", extra={"blob_name": myblob.name})
        logger.info("Processing blob size", extra={"blob_size": myblob.length})

        # (Insert your processing logic here)
        # Simulate reading the blob content (PDF bytes)
        pdf_bytes = myblob.read()

        # Simulate OCR extraction
        extracted_text = simulate_ocr(pdf_bytes)
        logger.info("OCR extraction complete", extra={"extracted_text": extracted_text})

        # Simulate ML model classification
        classification_result = simulate_ml_classification(extracted_text)
        logger.info(
            "ML classification complete",
            extra={"classification_result": classification_result})

        # Simulate writing the classification result to a database
        cosmost_response = simulate_write_to_db({
            "blob_name": myblob.name,
            "classification_result": classification_result,
            "extracted_text": extracted_text
        })
        logger.info("CosmosDB write simulated", extra=cosmost_response)

        # Optionally, add more details to the span if needed.
        span.add_attribute("blob_name", myblob.name)
        span.add_attribute("blob_size", myblob.length)
