#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

echo "🔹 Ensuring Azure authentication is correct..."

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Force logout to ensure a clean authentication session
echo "🔹 Logging out of Azure CLI to ensure fresh authentication..."
az logout || true

# Always use device code authentication
echo "🔹 Logging into Azure using device authentication (no browser required)..."
az login --use-device-code

# Set the correct subscription
echo "🔹 Verifying and setting the correct Azure subscription..."
CURRENT_SUBSCRIPTION=$(az account show --query "id" --output tsv 2>/dev/null || echo "")

if [[ "$CURRENT_SUBSCRIPTION" != "$AZURE_SUBSCRIPTION_ID" ]]; then
    echo "⚠️ Incorrect subscription detected! Expected: $AZURE_SUBSCRIPTION_ID but found: $CURRENT_SUBSCRIPTION"
    echo "🔹 Switching to the correct subscription..."
    az account set --subscription "$AZURE_SUBSCRIPTION_ID"
fi

echo "Using Subscription ID: $(az account show --query "id" --output tsv)"

echo "✅ Azure authentication verified and correct subscription confirmed."