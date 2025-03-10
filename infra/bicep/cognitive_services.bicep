targetScope = 'resourceGroup'

@description('Name of the Cognitive Services account (must be globally unique)')
param cognitiveServicesAccountName string

@description('Location for the Cognitive Services account')
param location string = resourceGroup().location

@description('SKU for the Cognitive Services account')
param skuName string = 'S0'

@description('The kind of Cognitive Services account. For OCR, "ComputerVision" is typical.')
param accountKind string = 'ComputerVision'

resource cognitiveServices 'Microsoft.CognitiveServices/accounts@2022-12-01' = {
  name: cognitiveServicesAccountName
  location: location
  sku: {
    name: skuName
  }
  kind: accountKind
  properties: {
    apiProperties: {}
  }
}

output cognitiveServicesEndpoint string = cognitiveServices.properties.endpoint
