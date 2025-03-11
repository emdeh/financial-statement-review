#!/bin/bash

set -e
set -o pipefail

# Load environment variables
set -o allexport; source infra/.env; set +o allexport

# Validate required environment variables for Event Grid provisioning
: "${AZURE_RESOURCE_GROUP:?Environment variable AZURE_RESOURCE_GROUP is required}"
: "${AZURE_STORAGE_ACCOUNT_NAME:?Environment variable AZURE_STORAGE_ACCOUNT_NAME is required}"
: "${AZURE_EVENT_GRID_SUBSCRIPTION_NAME:?Environment variable AZURE_EVENT_GRID_SUBSCRIPTION_NAME is required}"
: "${AZURE_FUNCTION_APP_NAME:?Environment variable AZURE_FUNCTION_APP_NAME is required}"

# Check if Event Grid subscription already exists
if az eventgrid event-subscription show --name "$AZURE_EVENT_GRID_SUBSCRIPTION_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --topic-name "$AZURE_STORAGE_ACCOUNT_NAME" &>/dev/null; then
    echo "✅ Event Grid Subscription \"$AZURE_EVENT_GRID_SUBSCRIPTION_NAME\" already exists. Skipping creation."

else
    # Retrieve the resource IDs for the Storage Account and the Function App
    FUNCTION_APP_RESOURCE_ID=$(az functionapp show --name "$AZURE_FUNCTION_APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --query "id" --output tsv)

    echo "🔹 Creating Event Grid Subscription \"$AZURE_EVENT_GRID_SUBSCRIPTION_NAME\" for Storage Account \"$AZURE_STORAGE_ACCOUNT_NAME\" triggering Function App \"$AZURE_FUNCTION_APP_NAME\""

    az deployment group create \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --template-file "$(pwd)/infra/bicep/event_grid.bicep" \
        --parameters eventSubscriptionName="$AZURE_EVENT_GRID_SUBSCRIPTION_NAME" storageAccountName="$AZURE_STORAGE_ACCOUNT_NAME" azureFunctionResourceId="$FUNCTION_APP_RESOURCE_ID"
fi

echo "✅ Event Grid Subscription setup complete!"

# infra/scripts/4_provision_event_grid.sh