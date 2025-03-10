# Bash script to deploy Azure resources
# This script will call individual scripts to enahnce modularity

# Reference Infra scripts in teh Infra folder

# Pre-check
echo "Running Azure Authentication"
bash infra/scripts/0_azure_auth.sh

# Deploy Resource Group
echo "Deploying Resource Group"
bash infra/scripts/1_create_rg.sh

# Deploy Storage Account
echo "Deploying Storage Account"
bash infra/scripts/2_provision_blob_storage.sh

# Provision Function App
echo "Provisioning Function App"
bash infra/scripts/3_provision_function.sh

# Provision event grid
#echo "Provisioning Event Grid"
#bash infra/scripts/4_provision_event_grid.sh
# TODO: Move the event grid provisioning after the function has been deployed

# Provision key vault
# echo "Provisioning Key Vault"
# sh ./infra/4_provision_azure_key_vault.sh

# Configure Managed Identity
# echo "Configuring Managed Identity"
# sh ./infra/5_configure_managed_ids.sh