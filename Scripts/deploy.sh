# Bash script to deploy Azure resources
# This script will call individual scripts to enahnce modularity

# Reference Infra scripts in teh Infra folder

# Deploy Resource Group
echo "Deploying Resource Group"
sh ./Infra/1_create_resource_group.sh

# Deploy Storage Account
echo "Deploying Storage Account"
sh ./Infra/2_provision_blob_storage.sh

# Provision event grid
echo "Provisioning Event Grid"
sh ./Infra/3_provision_event_grid.sh

# Provision key vault
echo "Provisioning Key Vault"
sh ./Infra/4_provision_azure_key_vault.sh

# Configure Managed Identity
echo "Configuring Managed Identity"
sh ./Infra/5_configure_managed_ids.sh