#!/bin/bash

set -e  # Stop on first error
set -o pipefail  # Capture pipeline errors

# Load environment variables before using them
set -o allexport; source infra/.env; set +o allexport

## TO DO: Bash script to provision blob storage + bicep template in resource_group.bicep

echo "🔹 Checking if Storage Account \"$AZURE_STORAGE_ACCOUNT_NAME\" exists..."