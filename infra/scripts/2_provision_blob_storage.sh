#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables before using them
set -o allexport; source infra/.env; set +o allexport

## TO DO: Bash script to provision blob storage + bicep template in resource_group.bicep

echo "🔹 Checking if Storage Account \"$AZURE_STORAGE_ACCOUNT_NAME\" exists..."

# Check if the storage account exists
if az storage account check-name --name "$AZURE_STORAGE_ACCOUNT_NAME" --query "nameAvailable" --output tsv | grep -q 'false'; then
    echo "🔹 Storage Account \"$AZURE_STORAGE_ACCOUNT_NAME\" already exists. Skipping creation."
else
    echo "🔹 Storage Account \"$AZURE_STORAGE_ACCOUNT_NAME\" does not exist. Creating..."
    az deployment group create \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --template-file "$(pwd)/infra/bicep/blob_storage.bicep" \
        --parameters storageAccountName="$AZURE_STORAGE_ACCOUNT_NAME"
fi

echo "✅ Blob Account setup complete!"