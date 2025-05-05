"""
ProcessPDF/main.py
Blob-triggered Azure Function that ingests a PDF, extracts text (embedded or
OCR), enriches it with Retrieval-Augmented Generation (RAG) checks, and writes
a structured result to Cosmos DB for downstream analytics.
"""

import os
import time
import azure.functions as func
from services.logger import Logger
from services.tracer import AppTracer
from services.ocr_service import OcrService, OcrServiceError
from services.debug_utils import write_debug_file, is_debug_mode
from services.pdf_utils import PDFService
from services.db_service import DbService
from services.rag_llm.embedding_service import EmbeddingService
from services.rag_llm.check_runner import run_llm_checks

# Initialise the JSON logger for this function
logger = Logger.get_logger("ProcessPDF", json_format=True)

# Retrieve the Application Insights instrumentation key from an environment variable
instrumentation_key = os.environ.get(
    "APPINSIGHTS_INSTRUMENTATIONKEY",
    "your_instrumentation_key_here"
    )

# Initialise the tracer with the instrumentation key
tracer = AppTracer(instrumentation_key)

def simulate_ml_classification(text):
    """
    Simulates a machine learning classification model.
    """
    return {
        "is_valid_afs": True,
        "afs_confidence": 0.95,
        "ml_message": "The document is valid and meets the AFS requirements."
    }

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

        # Invoke DbService to store results
        db = DbService()

        # Invoke PDFService to extract embedded text
        pdf_service = PDFService()

        # Read blob content (PDF bytes)
        pdf_bytes = myblob.read()

        # Check One: PDF validity check
        is_pdf = pdf_service.is_pdf(pdf_bytes)
        if not is_pdf:
            logger.error(
                "Blob is not a valid PDF file",
                extra={"blob_name": myblob.name}
            )
            db.store_results(
                document_name=myblob.name,
                data={
                    "isPDF": False,
                    "blobUrl": myblob.uri
                }
            )
            return

        logger.info("Blob is a valid PDF file", extra={"blob_name": myblob.name})

        # DEBUG
        if is_debug_mode():
            write_debug_file(
                {"isPDF": is_pdf},
                prefix="debug_is_pdf"
            )

        # Check Two: PDF page count check
        page_count = pdf_service.get_page_count(pdf_bytes)
        logger.info(
            "PDF page count",
            extra={
                "blob_name": myblob.name,
                "pageCount": page_count
            }
        )
        if page_count < 5 or page_count > 25:
            logger.warning(
                "Blob is unusually short or long with %d pages",
                page_count,
                extra={
                    "blob_name": myblob.name,
                    "pageCount": page_count
                }
            )
            db.store_results(
                document_name=myblob.name,
                data={
                    "isPDF": True,
                    "pageCount": page_count,
                    "blobUrl": myblob.uri
                }
            )
            return

        # DEBUG
        if is_debug_mode():
            write_debug_file(
                {"pageCount": page_count},
                prefix="debug_page_count"
            )

        # First attempt to extract embedded text for digitally generated PDFs
        embedded_pages = pdf_service.extract_embedded_text(pdf_bytes)

        if embedded_pages:
            extraction_method = "embedded"
            logger.info("Extraction complete using %s method",extraction_method,
            extra={
                "method": extraction_method,
                })
            extraction_pages = embedded_pages

        else:
            extraction_method = "OCR"
            logger.info("No embedded text found. Falling back to OCR...")

            # Extract using OCR
            try:
                ocr_pages = OcrService().extract_text(pdf_bytes)
                logger.info("Extraction complete using %s method", extraction_method,
                extra={
                    "method": extraction_method,
                    })
                extraction_pages = ocr_pages

            except OcrServiceError as e:
                logger.error("Error extracting text from PDF using %s", extraction_method,
                extra={
                    "error": str(e)
                    })
                return

        # Check Three: ABN detection
        full_text = "\n".join(extraction_pages.values())
        abn_value = pdf_service.find_abn(full_text)
        has_abn = abn_value is not None

        logger.info(
            "ABN detection complete",
            extra={
                "hasABN": has_abn,
                "ABN": abn_value
            }
        )

        # DEBUG
        if is_debug_mode():
            write_debug_file(
                {"hasABN": has_abn, "ABN": abn_value},
                prefix="debug_abn_detection"
            )

        # DEBUG
        if is_debug_mode():
            # Write the extracted text to a debug file
            debug_file = write_debug_file(extraction_pages, prefix="ocr_output")
            logger.info("DEBUG ON - Debug file written",
            extra={
                "method": extraction_method,
                "debug_file": debug_file
                })
            logger.info("Extraction method used was %s", extraction_method)

        logger.info("Continue processing...")
        # Continue processing (e.g., parse text, send to ML, etc)

        # Simulate ML model classification
        classification_result = simulate_ml_classification(full_text)
        logger.info(
            "ML classification complete",
            extra={"classification_result": classification_result})

        # DEBUG
        if is_debug_mode():
            # Dump the ML payload to a file
            debug_payload = {
                "extractionMethod": extraction_method,
                "classificationResult": classification_result
            }
            debug_file = write_debug_file(str(debug_payload), prefix="classification_payload")
            logger.info("DEBUG ON - Classification payload written",
            extra={
                "debug_file": debug_file
                })

        # --- RAG+LLM INTEGRATION POINT --- #

        embedding_service = EmbeddingService()
        embedding_service.index_chunks(
            document_name=myblob.name,
            page_texts=extraction_pages
            )

        # Add a delay of 20 seconds to allow for indexing
        # TODO: is this still needed?
        time.sleep(20)


        # Check Four: RAG Checks
        # Run all checks via check_runner
        llm_flags = run_llm_checks(
            document_name=myblob.name,
            system_prompt=None
        )

        # Construct the base payload
        base_payload = {
            "isPDF": is_pdf,
            "pageCount": page_count,
            "blobUrl": myblob.uri,
            "extractionMethod": extraction_method,
            "isValidAFS": classification_result["is_valid_afs"],
            "afsConfidence": classification_result["afs_confidence"],
            "hasABN": has_abn,
            "ABN": abn_value
        }

        # Build final payload by merging RAG results with base payload
        final_payload = {
            **base_payload,
            **llm_flags
        }

        # Write results to database
        try:
            db.store_results(
                document_name=myblob.name,
                data=final_payload
            )
        except Exception as e:
            logger.error("Error storing results in Cosmos DB",
            extra={
                "error": str(e)
                })
            return

        # Optionally, add more details to the span if needed.
        span.add_attribute("blob_name", myblob.name)
        span.add_attribute("blob_size", myblob.length)
        span.add_attribute("page_count", page_count)
        span.add_attribute("extraction_method", extraction_method)
