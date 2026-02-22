// ──────────────────────────────────────────────
// RBAC Role Assignments
// ──────────────────────────────────────────────

@description('Principal ID of the managed identity to assign roles to')
param principalId string

@description('Resource ID of the AI Services account')
param aiServicesAccountId string

@description('Resource ID of the agent storage account')
param agentStorageAccountId string

// ── Built-in Role Definition IDs ──
var cognitiveServicesContributorRoleId = '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68'
var cognitiveServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'
var cognitiveServicesOpenAIContributorRoleId = 'a001fd3d-188f-4b5d-821b-7da978bf7442'
var storageQueueDataContributorRoleId = '974c5e8b-45b9-4653-ba55-5f855dd0fb88'

// ── Cognitive Services Contributor ──
resource csContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServicesAccountId, principalId, cognitiveServicesContributorRoleId)
  scope: aiServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesContributorRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// ── Cognitive Services User ──
resource csUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServicesAccountId, principalId, cognitiveServicesUserRoleId)
  scope: aiServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// ── Cognitive Services OpenAI Contributor ──
resource csOpenAIContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServicesAccountId, principalId, cognitiveServicesOpenAIContributorRoleId)
  scope: aiServicesAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesOpenAIContributorRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// ── Reference existing AI Services account for scoping ──
resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: last(split(aiServicesAccountId, '/'))
}

// ── Reference existing agent storage account ──
resource agentStorageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: last(split(agentStorageAccountId, '/'))
}

// ── Storage Queue Data Contributor (for Foundry agents to send/receive messages) ──
resource storageQueueRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(agentStorageAccountId, principalId, storageQueueDataContributorRoleId)
  scope: agentStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageQueueDataContributorRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}
