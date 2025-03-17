targetScope = 'resourceGroup'

@description('Name of the Cognitive Services account (must be globally unique)')
param cognitiveServicesAccountName string

@description('Location for the Cognitive Services account')
param location string = resourceGroup().location

@allowed([
  'S0'
])
param skuName string = 'S0'

resource cognitiveServices 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: cognitiveServicesAccountName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: skuName
  }
  kind: 'ComputerVision'
  properties: {
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
    }
    disableLocalAuth: false
  }
}

output cognitiveServicesEndpoint string = cognitiveServices.properties.endpoint
