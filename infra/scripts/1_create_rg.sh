#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables before using them
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_LOCATION:?Environment variable AZURE_LOCATION is required}"

# Check if the resource group exists
echo "🔹 Checking if Resource Group \"$AZURE_RESOURCE_GROUP\" exists..."

# If exists, skip creation
if az group show --name "$AZURE_RESOURCE_GROUP" &>/dev/null; then
    echo "✅ Resource Group \"$AZURE_RESOURCE_GROUP\" already exists. Skipping creation."

# If not exists, create it
else
    echo "🔹 Resource Group \"$AZURE_RESOURCE_GROUP\" does not exist. Creating it now..."
    az deployment sub create \
        --location "$AZURE_LOCATION" \
        --template-file "$(pwd)/infra/bicep/resource_group.bicep" \
        --parameters location="$AZURE_LOCATION" resourceGroupName="$AZURE_RESOURCE_GROUP"

fi

echo "✅ Resource Group setup complete!"

# infra/scripts/1_create_rg.sh