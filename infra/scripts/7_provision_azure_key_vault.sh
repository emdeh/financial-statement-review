#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Key Vault provisioning
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_LOCATION:?Environment variable AZURE_LOCATION is required}"
: "${AZURE_KEY_VAULT_NAME:?Environment variable AZURE_KEY_VAULT_NAME is required}"
: "${AZURE_TENANT_ID:?Environment variable AZURE_TENANT_ID is required}"

echo "🔹 Checking if Azure Key Vault \"$AZURE_KEY_VAULT_NAME\" exists in Resource Group \"$AZURE_RESOURCE_GROUP\"..."

# Check if the Key Vault exists
if az keyvault show --name "$AZURE_KEY_VAULT_NAME" --resource-group "$AZURE_RESOURCE_GROUP" &>/dev/null; then
    echo "✅ Azure Key Vault \"$AZURE_KEY_VAULT_NAME\" already exists. Skipping creation."

else

    echo "🔹 Deploying Azure Key Vault \"$AZURE_KEY_VAULT_NAME\" in Resource Group \"$AZURE_RESOURCE_GROUP\"..."

    az deployment group create \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --template-file "$(pwd)/infra/bicep/key_vault.bicep" \
        --parameters keyVaultName="$AZURE_KEY_VAULT_NAME" location="$AZURE_LOCATION" tenantId="$AZURE_TENANT_ID"

fi

echo "✅ Azure Key Vault deployment complete!"

# infra/scripts/7_provision_azure_key_vault.sh