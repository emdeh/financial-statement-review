targetScope = 'resourceGroup'

@description('The name of the AML Workspace for the Document Classifier')
param workspaceName string

@description('The name of the online endpoint for the Document Classifier')
param endpointName string

@description('Location for the resources')
param location string = resourceGroup().location

@description('Existing Key Vault name')
param keyVaultName string

@description('Existing Storage Account name')
param storageAccountName string

@description('Application Insights name')
param appInsightsName string

// Create Application Insights resource first
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

// Create the AML Workspace
resource amlWorkspace 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: workspaceName
  identity: {
    type: 'SystemAssigned'
  }
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    friendlyName: workspaceName
    description: 'AML Workspace for hosting the Document Classifier service.'
    keyVault: resourceId('Microsoft.KeyVault/vaults', keyVaultName)
    storageAccount: resourceId('Microsoft.Storage/storageAccounts', storageAccountName)
    applicationInsights: resourceId('Microsoft.Insights/components', appInsightsName)
  }
}

/*
// Create the Online Endpoint
resource onlineEndpoint 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2024-10-01' = {
  parent: amlWorkspace
  identity: {
    type: 'SystemAssigned'
  }
  name: endpointName
  location: location
  properties: {
    authMode: 'Key'
    description: 'Online endpoint for the Document Classifier service.'
    //compute: 'Standard'
    // Additional properties (like deployment configuration) can be added as needed
  }
}
*/
output amlWorkspaceId string = amlWorkspace.id
//output onlineEndpointId string = onlineEndpoint.id
output appInsightsId string = appInsights.id
