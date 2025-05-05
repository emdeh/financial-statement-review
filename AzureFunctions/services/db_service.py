"""
services/db_service.py
Module for database service to handle database operations.

This module provides a service class to interact with Azure Cosmos DB for
storing and retrieving document processing results. It includes methods for
upserting items into the database and handling exceptions.

Classes:
--------
    DbService: A service class to handle database operations.

"""

import os
import uuid
from datetime import datetime
from azure.cosmos import CosmosClient, exceptions
from services.logger import Logger
from services.debug_utils import write_debug_file, is_debug_mode
from services.db_models import DocumentResult

class DbService:
    """
    A service class to handle database operations.
    This class interacts with Azure Cosmos DB to store and retrieve
    document processing results.

    Attributes
    ----------
        logger (Logger): Logger instance for logging messages.
        key (str): Key for authenticating with Azure Cosmos DB.
        account_uri (str): URI of the Cosmos DB account.
        database_name (str): Name of the Cosmos DB database.
        container_name (str): Name of the Cosmos DB container.
        client (CosmosClient): Cosmos DB client instance.
        database (Database): Cosmos DB database client instance.
        container (Container): Cosmos DB container client instance.        

    Methods
    ----------
        __init__():
            Initializes the DbService instance and connects to Cosmos DB.
        store_results(document_name: str, data: dict) -> dict:
            Stores the classification result in the Cosmos DB container.
    """
    def __init__(self):
        """
        Initialises the DbService instance and connects to Cosmos DB.
        """
        # Initialise the JSON logger for this service
        self.logger = Logger.get_logger("DbService", json_format=True)

        # Get key
        key = os.environ.get("COSMOS_KEY")

        # Read Cosmos DB configuration from environment variables
        self.account_uri = os.environ.get("COSMOS_ACCOUNT_URI")
        self.database_name = os.environ.get("COSMOS_DATABASE_NAME")
        self.container_name = os.environ.get("COSMOS_CONTAINER_NAME")

        # Validate config
        if not all([self.account_uri, self.database_name, self.container_name]):
            self.logger.error("Missing Cosmos DB configuration. Check environment variables.")
            raise ValueError("Missing Cosmos DB configuration. Check environment variables.")

        # Authenticate with Azure AD
        self.client = CosmosClient(self.account_uri, credential=key)
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

        Raises:
            exceptions.CosmosHttpResponseError: 
                If there is an error during the upsert operation.
            
        """
        # Log entry and key metadata
        self.logger.info(
            "Storing results to Cosmos DB",
            extra={
                "documentName": document_name,
                "fields": data.keys(),
            }
        )

        # Build the raw payload
        raw = {
            "id": str(uuid.uuid4()),  # Generate a unique ID for the document
            "documentName": document_name,
            "timestamp": datetime.utcnow(),
            **data
        }

        # DEBUG
        if is_debug_mode():
            write_debug_file(raw, prefix="cosmos_raw")

       # Validate & coerce via Pydantic
        validated_item = DocumentResult(**raw).model_dump(
            mode="json",
            by_alias=True,
        )

        # DEBUG
        if is_debug_mode():
            write_debug_file(validated_item, prefix="cosmos_validated")

        # 5) Upsert into Cosmos
        try:
            result = self.container.upsert_item(validated_item)
            self.logger.info(
                "Successfully stored results to Cosmos DB",
                extra={"documentName": document_name, "item_id": validated_item["id"]}
            )
            return result

        except exceptions.CosmosHttpResponseError as e:
            self.logger.exception(
                "Failed to upsert item to Cosmos DB",
                extra={
                    "documentName": document_name,
                    "status_code": e.status_code,
                    "error": e.message
                }
            )
            raise

        # DEBUG
        if is_debug_mode():
            write_debug_file(result, prefix="cosmos_response")
