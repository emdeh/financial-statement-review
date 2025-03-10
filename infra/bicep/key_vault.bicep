targetScope = 'resourceGroup'

@description('The name of the Key Vault (must be globally unique)')
param keyVaultName string

@description('The location for the Key Vault')
param location string = resourceGroup().location

@description('The Azure AD tenant ID for the Key Vault')
param tenantId string

@description('The SKU name for the Key Vault')
param skuName string = 'standard'

resource keyVault 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: tenantId
    sku: {
      family: 'A'
      name: skuName
    }
    accessPolicies: [] // You can populate with specific access policies if needed
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
  }
}

output keyVaultUri string = keyVault.properties.vaultUri
