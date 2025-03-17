#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Cognitive Services provisioning
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_LOCATION:?Environment variable AZURE_LOCATION is required}"
: "${AZURE_COMPUTER_VISION_ACCOUNT_NAME:?Environment variable AZURE_COMPUTER_VISION_ACCOUNT_NAME is required}"

# Check if the Cognitive Services account exists
echo "🔹 Checking if Computer Vision Account \"$AZURE_COMPUTER_VISION_ACCOUNT_NAME\" exists in Resource Group \"$AZURE_RESOURCE_GROUP\"..."

if az cognitiveservices account show --name "$AZURE_COMPUTER_VISION_ACCOUNT_NAME" --resource-group "$AZURE_RESOURCE_GROUP" &>/dev/null; then
    echo "✅ Computer Vision Account \"$AZURE_COMPUTER_VISION_ACCOUNT_NAME\" already exists. Skipping creation."

else
    echo "🔹 Deploying Computer Vision account \"$AZURE_COMPUTER_VISION_ACCOUNT_NAME\" in Resource Group \"$AZURE_RESOURCE_GROUP\"..."

    az deployment group create \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --template-file "$(pwd)/infra/bicep/computer_vision.bicep" \
        --parameters computerVisionAccountName="$AZURE_COMPUTER_VISION_ACCOUNT_NAME" location="$AZURE_LOCATION"
fi

echo "✅ Computer Vision deployment complete!"

# infra/scripts/6_provision_computer_vision.sh