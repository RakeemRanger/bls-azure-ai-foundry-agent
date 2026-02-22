// ──────────────────────────────────────────────
// Storage Queue Connection for Foundry Project
// Allows agents to send/receive queue messages
// ──────────────────────────────────────────────

@description('Name of the existing AI Services account')
param accountName string

@description('Name of the existing Foundry project')
param projectName string

@description('Name for the storage connection')
param connectionName string = 'agent-queue-storage'

@description('Resource ID of the storage account')
param storageAccountId string

// ── Reference existing account & project ──
resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: accountName
}

resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' existing = {
  parent: aiServicesAccount
  name: projectName
}

// Extract storage account name from resource ID
var storageAccountName = last(split(storageAccountId, '/'))

// Reference the storage account to get endpoint
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

// ── Project-level Storage Connection (with Managed Identity / AAD) ──
resource storageConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: foundryProject
  name: connectionName
  properties: {
    category: 'AzureStorageAccount'
    target: storageAccount.properties.primaryEndpoints.blob
    authType: 'AAD'
    metadata: {
      ApiType: 'Azure'
      ResourceId: storageAccountId
      location: storageAccount.location
    }
  }
}

// ── Outputs ──
output connectionName string = storageConnection.name
output connectionId string = storageConnection.id
output queueEndpoint string = 'https://${storageAccountName}.queue.${environment().suffixes.storage}'
