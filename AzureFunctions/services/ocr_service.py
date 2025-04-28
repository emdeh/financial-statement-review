"""
    services/ocr_service.py
    Module for OCR service to extract text from blob data using Azure Cognitive Services OCR API.

    This module implements the OcrService class which retrieves configuration from environment
    variables and calls the OCR API in a secure and robust manner following best practices.
    Classes:
        OcrService: A service class to handle OCR operations.

"""

import os
from typing import Dict
import time
import requests
from services.logger import Logger

class OcrServiceError(Exception):
    """
    Custom exception class for OCR service errors.
    """
    pass

class OcrService:
    """
    A service class to handle OCR operations using the Azure Cognitive Services OCR API.

    This class retrieves the endpoint and subscription key from environment variables and
    implements a robust OCR extraction method that polls for the operation result.

    Methods:
        extract_text(blob_data: bytes) -> Dict[int, str]:
            Extracts text from the given blob data using OCR.
    """
    def __init__(self):
        """
        Initialises the OCR service with the endpoint and subscription key 
        from environment variables.
        """
        self.endpoint = os.environ["COMPUTER_VISION_ENDPOINT"]
        self.subscription_key = os.environ["COMPUTER_VISION_KEY"]
        self.logger = Logger.get_logger("OcrService", json_format=True)


        if not self.endpoint or not self.subscription_key:
            self.logger.error("Missing OCR configuration. Check environment variables.")

        # Ensure the endpoint does not end with a trailing slash.
        self.endpoint = self.endpoint.rstrip("/")

        # Construct the READ API URL for OCR.
        self.read_api_url = f"{self.endpoint}/vision/v3.2/read/analyze"
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/octet-stream"
        }

    def extract_text(
        self,
        blob_data: bytes,
        timeout: int = 60,
        poll_interval: float = 1.0) -> Dict[int, str]:
        """
        Extracts text from the given blob data using the Azure Cognitive Services OCR API.

        Args:
            blob_data (bytes): The binary data of the blob from which text 
            needs to be extracted.

            timeout (int, optional): Maximum time in seconds to wait for the 
            OCR process to complete.

            poll_interval (float, optional): Time in seconds between 
            status polls.

        Returns:
            Dict[int,str]: Mapping of page number → concatenated lines on that page.

        Raises:
            Exception: If the OCR API call fails, processing fails, or times out.
        """
        try:
            # Initiate the OCR operation
            response = requests.post(
                self.read_api_url,
                headers=self.headers,
                data=blob_data,
                timeout=10)

            if response.status_code != 202:
                raise OcrServiceError(
                    f"OCR API call failed with status code {response.status_code}: {response.text}"
                )

            # Get the Operation-Location header for polling the result
            operation_url = response.headers.get("Operation-Location")
            if not operation_url:
                raise OcrServiceError(
                    "Operation-Location header missing from OCR API response."
                )

            self.logger.debug("OCR API call accepted. Polling for result at %s", operation_url)

            # Poll for the OCR result until the status is 'succeeded' or until timeout
            elapsed_time = 0.0
            while elapsed_time < timeout:
                result_response = requests.get(
                    operation_url,
                    headers={"Ocp-Apim-Subscription-Key": self.subscription_key},
                    timeout=10)
                result_json = result_response.json()
                status = result_json.get("status")
                self.logger.debug("Polling status: %s", status)
                if status == "succeeded":
                    extracted_text = self._parse_read_results(result_json)
                    return extracted_text
                elif status == "failed":
                    raise OcrServiceError("OCR processing failed.")
                time.sleep(poll_interval)
                elapsed_time += poll_interval

            raise TimeoutError("OCR processing timed out.")
        except requests.RequestException as e:
            self.logger.error("OCR API request failed: %s", str(e))
            raise OcrServiceError(f"OCR API request failed: {str(e)}") from e

    def _parse_read_results(self, result_json: dict) -> Dict[int, str]:
        """
        Parses the OCR read results JSON and concatenates the extracted text.

        Args:
            result_json (dict): The JSON response from the OCR API.

        Returns:
            Dict[int,str]: Mapping of page number → concatenated lines on that page.
        """
        pages = result_json.get("analyzeResult", {}).get("readResults", [])
        page_texts: Dict[int, str] = {}
        for idx, page in enumerate(pages, start=1):
            lines = [ln.get("text", "") for ln in page.get("lines", [])]
            page_texts[idx] = "\n".join(lines)
        return page_texts

