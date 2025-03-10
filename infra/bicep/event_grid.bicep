targetScope = 'resourceGroup'

@description('The name of the Event Grid subscription')
param eventSubscriptionName string

@description('The resource ID of the Azure Function to trigger')
param azureFunctionResourceId string

@description('The name of the existing Storage Account')
param storageAccountName string

// Reference the existing Storage Account resource
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: storageAccountName
}

resource eventSubscription 'Microsoft.EventGrid/eventSubscriptions@2024-12-15-preview' = {
  name: eventSubscriptionName
  // Use the existing storage account resource as the scope
  scope: storageAccount
  properties: {
    destination: {
      endpointType: 'AzureFunction'
      properties: {
        resourceId: azureFunctionResourceId
      }
    }
    filter: {
      includedEventTypes: [
        'Microsoft.Storage.BlobCreated'
      ]
    }
  }
}

output eventSubscriptionId string = eventSubscription.id
