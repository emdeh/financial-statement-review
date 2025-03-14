import logging

def main(myblob: bytes, name: str):
    logging.info("Blob trigger function processed blob\nName: %s\nSize: %d bytes", name, len(myblob))
    # You can access metadata via additional parameters if defined in function.json.
