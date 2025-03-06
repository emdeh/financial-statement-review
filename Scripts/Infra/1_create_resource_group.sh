#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables BEFORE using them
set -o allexport; source infra/.env; set +o allexport

echo "🔹 Checking if Resource Group \"$AZURE_RESOURCE_GROUP\" exists..."

# Check if the resource group exists
if az group show --name "$AZURE_RESOURCE_GROUP" &>/dev/null; then
    echo "✅ Resource Group \"$AZURE_RESOURCE_GROUP\" already exists. Skipping creation."
else
    echo "🔹 Resource Group \"$AZURE_RESOURCE_GROUP\" does not exist. Creating it now..."
    az deployment sub create \
        --location "$AZURE_LOCATION" \
        --template-file "$(pwd)/infra/main.bicep" \
        --parameters location="$AZURE_LOCATION" resourceGroupName="$AZURE_RESOURCE_GROUP"

fi

echo "✅ Resource Group setup complete!"