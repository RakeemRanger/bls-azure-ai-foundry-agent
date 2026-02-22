// ──────────────────────────────────────────────
// RBAC Role Assignments for Function App
// Grants permissions to Storage and AI Services
// ──────────────────────────────────────────────

@description('Principal ID of the Function App managed identity')
param functionAppPrincipalId string

@description('Resource ID of the storage account for Function App backend')
param functionStorageAccountId string

@description('Resource ID of the storage account with agent queues')
param agentStorageAccountId string

@description('Resource ID of the AI Services account')
param aiServicesAccountId string

// ── Built-in Role Definition IDs ──

// Storage roles
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var storageQueueDataContributorRoleId = '974c5e8b-45b9-4653-ba55-5f855dd0fb88'
var storageTableDataContributorRoleId = '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3'

// AI Services roles
var cognitiveServicesContributorRoleId = '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68'
var cognitiveServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'
var cognitiveServicesOpenAIContributorRoleId = 'a001fd3d-188f-4b5d-821b-7da978bf7442'
var azureAiUserRoleId = '53ca6127-db72-4b80-b1b0-d745d6d5456d'
// ── Reference Storage Accounts ──
resource functionStorageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: last(split(functionStorageAccountId, '/'))
}

resource agentStorageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: last(split(agentStorageAccountId, '/'))
}

// ── Reference AI Services Account ──
resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: last(split(aiServicesAccountId, '/'))
}

// ── Storage Blob Data Contributor (Function Storage) ──
resource funcStorageBlobRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(functionStorageAccountId, functionAppPrincipalId, storageBlobDataContributorRoleId)
  scope: functionStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ── Storage Queue Data Contributor (Function Storage) ──
resource funcStorageQueueRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(functionStorageAccountId, functionAppPrincipalId, storageQueueDataContributorRoleId)
  scope: functionStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageQueueDataContributorRoleId)
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ── Storage Table Data Contributor (Function Storage) ──
resource funcStorageTableRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(functionStorageAccountId, functionAppPrincipalId, storageTableDataContributorRoleId)
  scope: functionStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageTableDataContributorRoleId)
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ── Storage Queue Data Contributor (Agent Storage) ──
resource agentStorageQueueRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(agentStorageAccountId, functionAppPrincipalId, storageQueueDataContributorRoleId)
  scope: agentStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageQueueDataContributorRoleId)
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ── Cognitive Services Contributor ──
resource csContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServicesAccountId, functionAppPrincipalId, cognitiveServicesContributorRoleId)
  scope: aiServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesContributorRoleId)
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ── Cognitive Services User ──
resource csUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServicesAccountId, functionAppPrincipalId, cognitiveServicesUserRoleId)
  scope: aiServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ── Cognitive Services OpenAI Contributor ──
resource csOpenAIContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServicesAccountId, functionAppPrincipalId, cognitiveServicesOpenAIContributorRoleId)
  scope: aiServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesOpenAIContributorRoleId)
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}
