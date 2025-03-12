# Main processing logic
import logging
import azure.functions as func


app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="pdf-uploads/{name}",
                               connection="ca9ed4_STORAGE") 
def ProcessPDFBlob(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
