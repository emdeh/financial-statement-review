"""
    Main entry point for the Azure Function.
    This function is triggered by a blob trigger and logs the name and size of the blob.
"""

import logging

def main(myblob: bytes, name: str):
    """
    Main entry point for the Azure Function.
    """
    logging.info(
        "Blob trigger function processed blob\nName: %s\nSize: %d bytes",
         name, len(myblob))
    # You can access metadata via additional parameters if defined in function.json.
