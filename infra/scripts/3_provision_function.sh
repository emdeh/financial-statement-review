#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables before using them
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Azure Function provisioning
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_LOCATION:?Environment variable AZURE_LOCATION is required}"
: "${AZURE_FUNCTION_APP_NAME:?Environment variable AZURE_FUNCTION_APP_NAME is required}"

echo "🔹 Checking if Azure Function App \"$AZURE_FUNCTION_APP_NAME\" exists in Resource Group \"$AZURE_RESOURCE_GROUP\"..."

# Check if the Function App exists
if az functionapp show --name "$AZURE_FUNCTION_APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" &>/dev/null; then
    echo "✅ Azure Function App \"$AZURE_FUNCTION_APP_NAME\" already exists. Skipping creation."

else
    echo "🔹 Azure Function App \"$AZURE_FUNCTION_APP_NAME\" does not exist. Creating it now..."
    az deployment group create \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --template-file "$(pwd)/infra/bicep/function_app.bicep" \
        --parameters functionAppName="$AZURE_FUNCTION_APP_NAME" location="$AZURE_LOCATION"
fi

# Retrieve and display the Function App's resource ID
FUNCTION_APP_RESOURCE_ID=$(az functionapp show --name "$AZURE_FUNCTION_APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --query "id" --output tsv)
echo "✅ Azure Function App resource ID: $FUNCTION_APP_RESOURCE_ID"

# infra/scripts/3_provision_function_.sh