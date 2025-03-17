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
