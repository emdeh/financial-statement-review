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
from services.ocr_service import OcrService, OcrServiceError
from services.debug_utils import write_debug_file, is_debug_mode
from services.pdf_utils import extract_embedded_text

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
#def simulate_ocr(pdf_bytes):
#    """
#    Simulates OCR processing on a PDF document.
#
#    """
#    return "Extracted text from PDF. This is a simulated OCR output."


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
        logger.info("Blob trigger function processed %s", myblob.name,
        extra={
            "blob_name": myblob.name
            })

        # Read blob content (PDF bytes)
        pdf_bytes = myblob.read()

        # First attempt to extracted embedded text for digitally generated PDFs
        embedded_text = extract_embedded_text(pdf_bytes)

        if embedded_text:
            extraction_method = "embedded"
            logger.info("Extraction complete using %s method",extraction_method,
            extra={
                "method": extraction_method,
                "extracted_text": embedded_text
                })

            logger.info("Extraction output length is %s", len(embedded_text))
            ocr_result = embedded_text

        else:
            extraction_method = "OCR"
            logger.info("No embedded text found. Falling back to OCR...")

            # Extract using OCR
            try:
                ocr_result = OcrService().extract_text(pdf_bytes)
                logger.info("Extraction complete using %s method", extraction_method,
                extra={
                    "method": extraction_method,
                    "extracted_text": ocr_result
                    })

                logger.info("Extraction output length is %s", len(ocr_result))

            except OcrServiceError as e:
                logger.error("Error extracting text from PDF using %s", extraction_method,
                extra={
                    "error": str(e)
                    })
                return

        if is_debug_mode():
            # Write the extracted text to a debug file
            debug_file = write_debug_file(ocr_result, prefix="ocr_output")
            logger.info("DEBUG ON - Debug file written",
            extra={
                "method": extraction_method,
                "debug_file": debug_file
                })
            logger.info("Extraction method used was %s", extraction_method)

        logger.info("Continue processing...")
        # Continue processing (e.g., parse text, send to ML, etc)

        # Simulate ML model classification
        classification_result = simulate_ml_classification(ocr_result)
        logger.info(
            "ML classification complete",
            extra={"classification_result": classification_result})

        # Simulate writing the classification result to a database
        cosmos_response = simulate_write_to_db({
            "blob_name": myblob.name,
            "classification_result": classification_result,
            "extracted_text": ocr_result
        })
        logger.info("CosmosDB write simulated", extra=cosmos_response)

        # Optionally, add more details to the span if needed.
        span.add_attribute("blob_name", myblob.name)
        span.add_attribute("blob_size", myblob.length)
