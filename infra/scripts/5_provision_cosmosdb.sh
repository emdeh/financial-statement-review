#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Cosmos DB provisioning
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_LOCATION:?Environment variable AZURE_LOCATION is required}"
: "${AZURE_COSMOS_DB_ACCOUNT_NAME:?Environment variable AZURE_COSMOS_DB_ACCOUNT_NAME is required}"
# Optionally, you can also add validations for the database and container names if you decide to make them configurable

echo "🔹 Deploying Azure Cosmos DB Account \"$AZURE_COSMOS_DB_ACCOUNT_NAME\"..."

az deployment group create \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --template-file "$(pwd)/infra/bicep/cosmosdb.bicep" \
    --parameters cosmosDbAccountName="$AZURE_COSMOS_DB_ACCOUNT_NAME" location="$AZURE_LOCATION"

echo "✅ Cosmos DB deployment complete!"

# infra/scripts/5_provision_cosmos_db.sh