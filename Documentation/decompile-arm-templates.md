# How to Decompile an ARM Template to a Bicep Template and Reference Deployment Variables

1. **Install Bicep:**
- Ensure  Azure CLI is updated and install Bicep:
     ```bash
     az bicep install
     az bicep version
     ```

2. **Decompile the ARM Template:**
- Deploy resources manually, then navigate to ***Automation > Export template*** in the resource's left-hand pane to export the confguration as an ARM template.
- Navigate to the directory containing your ARM template (e.g., `template.json`) and run:
     ```bash
     az bicep decompile --file template.json --force
     ```
- This command will generate a Bicep file (e.g., `template.bicep`) in the current directory and overwrite the existing file.

3. **Modify the Decompiled Bicep Template:**
- Edit the decompiled Bicep file to ensure it references parameters that will be passed in via the deployment script. For example:

     ```bicep
     targetScope = 'resourceGroup'

     @description('Name of the Cognitive Services account (must be globally unique)')
     param computerVisionAccountName string

     @description('Location for the Cognitive Services account')
     param location string = resourceGroup().location

     resource cognitiveServices 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
       name: computerVisionAccountName
       location: location
       sku: {
         name: 'F0'
       }
       kind: 'ComputerVision'
       identity: {
         type: 'None'
       }
       properties: {
         customSubDomainName: computerVisionAccountName
         networkAcls: {
           defaultAction: 'Allow'
           virtualNetworkRules: []
           ipRules: []
         }
         publicNetworkAccess: 'Enabled'
       }
     }

     output computerVisionAccountEndpoint string = cognitiveServices.properties.endpoint
     ```

4. **Reference Deployment Variables in Your Bash Script:**
- In the deployment script, source the environment variables from the `.env` file and pass them as parameters to the Bicep deployment. For example:

     ```bash
     #!/bin/bash

     set -e  # Stop on first error
     set -o pipefail  # Capture pipeline errors

     # Load environment variables from the .env file
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
     ```

Following these steps, you can decompile ARM templates into a Bicep template, modify it to use parameters (referenced via the `.env` file), and then deploy it using the bash script.
