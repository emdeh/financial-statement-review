"""
services/db_service.py
Module for database service to handle database operations.

Classes:
    DbService: A service class to handle database operations.

"""

import os
import uuid
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, exceptions
from services.logger import Logger
from services.debug_utils import write_debug_file, is_debug_mode

class DbService:
    """
    A service class to handle database operations.

    Methods:
        store_results(document_name: str, data: dict) -> dict:
            Stores the classification result in the Cosmos DB container.
    """
    def __init__(self):
        # Initialise the JSON logger for this service
        self.logger = Logger.get_logger("DbService", json_format=True)

        # Read Cosmos DB configuration from environment variables
        self.account_uri = os.getenv("COSMOS_ACCOUNT_URI")
        self.database_name = os.getenv("COSMOS_DATABASE_NAME")
        self.container_name = os.getenv("COSMOS_CONTAINER_NAME")

        # Validate config
        if not all([self.account_uri, self.database_name, self.container_name]):
            self.logger.error("Missing Cosmos DB configuration. Check environment variables.")
            raise ValueError("Missing Cosmos DB configuration. Check environment variables.")

        # Authenticate with Azure AD
        credential = DefaultAzureCredential()
        self.client = CosmosClient(self.account_uri, credential=credential)
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)
        self.logger.info("Connected to Cosmos DB successfully.")

        # DEBUG
        if is_debug_mode():
            # Log the configuration details for debugging
            # Note: Be cautious with logging sensitive information in production.S
            self.logger.info(
                "DEBUG ON – Cosmos config",
                extra={
                    "accountUri": self.account_uri,
                    "database": self.database_name,
                    "container": self.container_name
                    }
                    )


    def store_results(self, document_name: str, data: dict) -> dict:
        """
        Stores the classification result in the Cosmos DB container.

        Args:
            document_name (str): The name of the processed document (blob name).
            data (dict): A dictionary containing the result data to store.

        Returns:
            dict: The upserted item from Cosmos DB.
        """
        # Log entry and key metadata
        self.logger.info(
            "Storing results to Cosmos DB",
            extra={
                "documentName:": document_name,
                "fields": data.keys(),
            }
        )

        # Build the base item
        item = {
            "id": str(uuid.uuid4()),  # Generate a unique ID for the document
            "documentName": document_name,
            "blobUrl": data.get("blobUrl"),
            "extractionMethod": data.get("extractionMethod"),
            "isValidAFS": data.get("is_valid_afs"),
            "confidence": data.get("confidence"),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Include any additional fields provided
        for key, value in data.items():
            if key not in item:
                item[key] = value

        # DEBUG
        if is_debug_mode():
            # Write the item to a debug file
            debug_file = write_debug_file(item, prefix="cosmos_item")
            self.logger.info(
                "DEBUG ON – Cosmos DB item payload written",
                extra={"debug_file": debug_file}
                )

        # Upsert into Cosmos DB
        try:
            result = self.container.upsert_item(item)
            return result
        except exceptions.CosmosHttpResponseError as e:
            # Log full exception with stack trace
            self.logger.exception(
                "Failed to upsert item to Cosmos DB",
                extra={
                    "documentName": document_name,
                    "status_code": e.status_code,
                    "error": e.message
                }
            )
            raise
        self.logger.info(
            "Successfully stored results to Cosmos DB",
            extra={
                "documentName": document_name,
                "item_id": item["id"]
            }
        )
