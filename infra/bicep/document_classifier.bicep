targetScope = 'resourceGroup'

@description('The name of the AML Workspace for the Document Classifier')
param workspaceName string

@description('The name of the online endpoint for the Document Classifier')
param endpointName string

@description('Location for the resources')
param location string = resourceGroup().location

resource amlWorkspace 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: workspaceName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    friendlyName: workspaceName
    description: 'AML Workspace for hosting the Document Classifier service.'
  }
}

resource onlineEndpoint 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2024-10-01' = {
  parent: amlWorkspace
  name: endpointName
  location: location
  properties: {
    authMode: 'Key'
    description: 'Online endpoint for the Document Classifier service.'
    compute: 'Standard'
    // Additional properties (like deployment configuration) can be added as needed
  }
}

output amlWorkspaceId string = amlWorkspace.id
output onlineEndpointId string = onlineEndpoint.id
