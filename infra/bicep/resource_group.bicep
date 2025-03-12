targetScope = 'subscription'

param location string
param resourceGroupName string

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-11-01' = {
  name: resourceGroupName
  location: location
}
