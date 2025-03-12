#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Managed Identity configuration
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_FUNCTION_APP_NAME:?Environment variable AZURE_FUNCTION_APP_NAME is required}"
: "${AZURE_KEY_VAULT_NAME:?Environment variable AZURE_KEY_VAULT_NAME is required}"

echo "🔹 Checking if Function App '$AZURE_FUNCTION_APP_NAME' has a system-managed identity..."

# Check if the function app already has an identity assigned
EXISTING_IDENTITY=$(az functionapp show --name "$AZURE_FUNCTION_APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --query "identity.principalId" --output tsv || echo "")

if [ -z "$EXISTING_IDENTITY" ]; then
    echo "🔹 No system-managed identity found. Assigning one..."
    ASSIGNED_IDENTITY=$(az functionapp identity assign --name "$AZURE_FUNCTION_APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --query principalId --output tsv)
    echo "✅ Managed identity assigned. Principal ID: $ASSIGNED_IDENTITY"

else
    echo "✅ System-managed identity already assigned. Principal ID: $EXISTING_IDENTITY"
    ASSIGNED_IDENTITY="$EXISTING_IDENTITY"

fi

echo "🔹 Checking if Key Vault '$AZURE_KEY_VAULT_NAME' already has an access policy for the managed identity..."

# Check if the Key Vault already has an access policy for this identity
ACCESS_POLICY=$(az keyvault show --name "$AZURE_KEY_VAULT_NAME" --query "properties.accessPolicies[?objectId=='$ASSIGNED_IDENTITY']" --output json)

if [[ "$ACCESS_POLICY" == "[]" ]]; then
    echo "🔹 No access policy found for Principal ID: $ASSIGNED_IDENTITY. Setting access policy..."
    az keyvault set-policy --name "$AZURE_KEY_VAULT_NAME" \
      --object-id "$ASSIGNED_IDENTITY" \
      --secret-permissions get list
    echo "✅ Key Vault access policy updated for managed identity."

else
    echo "✅ Key Vault already has an access policy for managed identity (Principal ID: $ASSIGNED_IDENTITY)."

fi

echo "✅ Managed identity configuration complete!"

# infra/scripts/8_configure_managed_ids.sh
