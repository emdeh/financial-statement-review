"""
    main.py
    Main entry point for the Azure Function.
    This function is triggered by a blob trigger and logs the name and size of the blob.
"""

import logging
import azure.functions as func

def main(myblob: func.InputStream):
    """
    Main entry point for the Azure Function.
    """
    logging.info("Blob trigger function processed blob")
    logging.info("Name: %s", myblob.name)
    #logging.info("Size: %d bytes", myblob.length)
    # You can access metadata via additional parameters if defined in function.json.
