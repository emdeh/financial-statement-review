import logging

def main(myblob: bytes, name: str):
    logging.info(f"Blob trigger function processed blob\nName: {name}\nSize: {len(myblob)} bytes")
    # You can access metadata via additional parameters if defined in function.json.
