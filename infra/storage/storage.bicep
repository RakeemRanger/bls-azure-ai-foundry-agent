// ──────────────────────────────────────────────
// Storage Account with Queues
// ──────────────────────────────────────────────

@description('Name of the storage account')
param storageAccountName string

@description('Deployment location')
param location string = resourceGroup().location

@description('Array of queue names to create')
param queueNames array = []

// ── Storage Account ──
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
    }
  }
}

// ── Queue Service ──
resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {}
}

// ── Queues (dynamic based on queueNames array) ──
resource queues 'Microsoft.Storage/storageAccounts/queueServices/queues@2023-01-01' = [
  for queueName in queueNames: {
    parent: queueService
    name: queueName
    properties: {
      metadata: {}
    }
  }
]

// ── Outputs ──
@description('The resource ID of the storage account')
output storageAccountId string = storageAccount.id

@description('The resource name of the storage account')
output storageAccountName string = storageAccount.name

@description('The primary endpoints for the storage account')
output primaryEndpoints object = storageAccount.properties.primaryEndpoints

@description('The names of all created queues')
output queueNames array = queueNames
