#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Cognitive Services provisioning
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_LOCATION:?Environment variable AZURE_LOCATION is required}"
: "${AZURE_COGNITIVE_SERVICES_ACCOUNT_NAME:?Environment variable AZURE_COGNITIVE_SERVICES_ACCOUNT_NAME is required}"

echo "🔹 Deploying Cognitive Services account \"$AZURE_COGNITIVE_SERVICES_ACCOUNT_NAME\" in Resource Group \"$AZURE_RESOURCE_GROUP\"..."

az deployment group create \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --template-file "$(pwd)/infra/bicep/cognitive_services.bicep" \
    --parameters cognitiveServicesAccountName="$AZURE_COGNITIVE_SERVICES_ACCOUNT_NAME" location="$AZURE_LOCATION"

echo "✅ Cognitive Services deployment complete!"
