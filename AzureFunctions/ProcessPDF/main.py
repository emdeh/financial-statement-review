"""
    ProcessPDF/main.py
    Main entry point for the Azure Function.
    This function is triggered by a blob trigger and logs the name and size of the blob.
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

def main(myblob: func.InputStream):
    """
    Main entry point for the Azure Function.
    """
    with tracer.span(name="ProcessPDFOperation") as span:
        with tracer.span(name="ProcessPDFOperation") as span:
            # Log the beginning of the blob processing operation, including extra context.
            logger.info("Blob trigger function processed blob", extra={"blob_name": myblob.name})
            logger.info("Processing blob size", extra={"blob_size": myblob.length})

            # (Insert your processing logic here)
            # For example, process the PDF, extract text, perform classification, etc.

            # Optionally, add more details to the span if needed.
            span.add_attribute("blob_name", myblob.name)
            span.add_attribute("blob_size", myblob.length)
