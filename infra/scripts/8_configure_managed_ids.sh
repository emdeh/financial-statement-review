#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Managed Identity configuration
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_FUNCTION_APP_NAME:?Environment variable AZURE_FUNCTION_APP_NAME is required}"
: "${AZURE_KEY_VAULT_NAME:?Environment variable AZURE_KEY_VAULT_NAME is required}"

echo "🔹 Assigning system-managed identity to Function App \"$AZURE_FUNCTION_APP_NAME\" in Resource Group \"$AZURE_RESOURCE_GROUP\"..."

# Assign system-managed identity to the function app
IDENTITY_OUTPUT=$(az functionapp identity assign --name "$AZURE_FUNCTION_APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --query principalId --output tsv)
echo "✅ Managed identity assigned. Principal ID: $IDENTITY_OUTPUT"

echo "🔹 Configuring Key Vault access policy for the Function App managed identity..."

# Grant the function app's managed identity permission to read secrets from the Key Vault
az keyvault set-policy --name "$AZURE_KEY_VAULT_NAME" \
  --object-id "$IDENTITY_OUTPUT" \
  --secret-permissions get list

echo "✅ Key Vault access policy updated for managed identity."

# infra/scripts/8_configure_managed_ids.sh