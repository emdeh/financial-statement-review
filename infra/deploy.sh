#!/bin/bash

# Stop on first error
set -euo pipefail

# Bash script to deploy Azure resources
# This script will call individual scripts to enahnce modularity
# Reference scripts in the infra/ folder

# Pre-check
echo "Running Azure Authentication"
bash infra/scripts/0_azure_auth.sh

# Deploy Resource Group
echo "Deploying Resource Group"
bash infra/scripts/1_create_rg.sh

# Deploy Storage Account
# echo "Deploying Storage Account"
# bash infra/scripts/2_provision_blob_storage.sh

# Provision Function App
# echo "Provisioning Function App"
# bash infra/scripts/3_provision_function.sh

# Provision Function
# echo "Provisioning Function"
# TODO: Placeholder for function provisioning

# Provision event grid
# echo "Provisioning Event Grid"
# bash infra/scripts/4_provision_event_grid.sh
# TODO: Event Grid provisioning dependent on function being deployed.

# Provision Cosmos DB
# echo "Provisioning Cosmos DB"
# bash infra/scripts/5_provision_cosmosdb.sh

# Provision Computer Vision
echo "Provisioning Computer Vision"
bash infra/scripts/6_provision_computer_vision.sh

# Provision key vault
# echo "Provisioning Key Vault"
# bash infra/scripts/7_provision_azure_key_vault.sh

# Configure Managed Identity
# echo "Configuring Managed Identity"
# bash infra/scripts/8_configure_managed_ids.sh

# Provision Document Classifier
# echo "Provisioning Azure Machine Learning Workspace"
# bash infra/scripts/9_provision_aml_workspace.sh

# Complete message
echo "Azure resources deployed successfully!"