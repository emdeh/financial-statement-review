#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

echo "🔹 Ensuring Azure authentication is correct..."

# Validate required environment variables
: "${AZURE_SUBSCRIPTION_ID:?Environment variable AZURE_SUBSCRIPTION_ID is required}"

# Get the current subscription ID
CURRENT_SUBSCRIPTION=$(az account show --query "id" --output tsv 2>/dev/null || echo "")

# Check if the current subscription matches the environment variable
if [[ "$CURRENT_SUBSCRIPTION" != "$AZURE_SUBSCRIPTION_ID" ]]; then
    echo "⚠️ Incorrect subscription detected! Expected: $AZURE_SUBSCRIPTION_ID but found: $CURRENT_SUBSCRIPTION"
    echo "🔹 Switching to the correct subscription..."

    # Force logout to ensure a fresh authentication session
    echo "🔹 Logging out of Azure CLI to ensure fresh authentication..."
    az logout || true

    # Always use device code authentication
    echo "🔹 Logging into Azure using device authentication (no browser required)..."
    az login --use-device-code

    # Set the correct subscription
    echo "🔹 Setting the correct Azure subscription..."
    az account set --subscription "$AZURE_SUBSCRIPTION_ID"
else
    echo "✅ Correct subscription ($AZURE_SUBSCRIPTION_ID) is already set. No need for login."
fi

# Show the current subscription
echo "Using Subscription ID: $(az account show --query "id" --output tsv)"

echo "✅ Azure authentication verified and correct subscription confirmed."
