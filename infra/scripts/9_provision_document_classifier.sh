#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Document Classifier provisioning
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_LOCATION:?Environment variable AZURE_LOCATION is required}"
: "${AZURE_DOCUMENT_CLASSIFIER_WORKSPACE_NAME:?Environment variable AZURE_DOCUMENT_CLASSIFIER_WORKSPACE_NAME is required}"
: "${AZURE_DOCUMENT_CLASSIFIER_ENDPOINT_NAME:?Environment variable AZURE_DOCUMENT_CLASSIFIER_ENDPOINT_NAME is required}"
: "${AZURE_KEY_VAULT_NAME:?Environment variable AZURE_KEY_VAULT_NAME is required}"
: "${AZURE_STORAGE_ACCOUNT_NAME:?Environment variable AZURE_STORAGE_ACCOUNT_NAME is required}"
: "${AZURE_APP_INSIGHTS_NAME:?Environment variable AZURE_APP_INSIGHTS_NAME is required}"

echo "🔹 Checking if Document Classifier service \"$AZURE_DOCUMENT_CLASSIFIER_WORKSPACE_NAME\" exists..."

## Check if the Document Classifier service exists
if az ml workspace show --workspace-name "$AZURE_DOCUMENT_CLASSIFIER_WORKSPACE_NAME" &>/dev/null; then
    echo "✅ Document Classifier service \"$AZURE_DOCUMENT_CLASSIFIER_WORKSPACE_NAME\" already exists. Skipping creation."

else
    echo "🔹 Deploying Document Classifier service in AML workspace \"$AZURE_DOCUMENT_CLASSIFIER_WORKSPACE_NAME\"..."

    az deployment group create \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --template-file "$(pwd)/infra/bicep/document_classifier.bicep" \
        --parameters workspaceName="$AZURE_DOCUMENT_CLASSIFIER_WORKSPACE_NAME" \
                    endpointName="$AZURE_DOCUMENT_CLASSIFIER_ENDPOINT_NAME" \
                    location="$AZURE_LOCATION" \
                    keyVaultName="$AZURE_KEY_VAULT_NAME" \
                    storageAccountName="$AZURE_STORAGE_ACCOUNT_NAME" \
                    appInsightsName="$AZURE_APP_INSIGHTS_NAME"
fi

echo "✅ Document Classifier service deployed successfully!"
