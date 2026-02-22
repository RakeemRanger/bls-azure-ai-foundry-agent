// ──────────────────────────────────────────────
// AI Foundry Account + Project + RAI Policies
// ──────────────────────────────────────────────

@description('Name of the AI Services account')
param accountName string

@description('Deployment location')
param location string = resourceGroup().location

@description('Resource ID of the user-assigned managed identity')
param userAssignedIdentityId string

@description('Name of the Foundry project')
param projectName string

// ── AI Services Account ──
resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: accountName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    apiProperties: {}
    customSubDomainName: accountName
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    allowProjectManagement: true
    defaultProject: projectName
    associatedProjects: [
      projectName
    ]
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
}

// ── Defender for AI (disabled) ──
resource defenderSettings 'Microsoft.CognitiveServices/accounts/defenderForAISettings@2025-06-01' = {
  parent: aiServicesAccount
  name: 'Default'
  properties: {
    state: 'Disabled'
  }
}

// ── Foundry Project ──
resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: aiServicesAccount
  name: projectName
  location: location
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

// NOTE: Microsoft.Default and Microsoft.DefaultV2 RAI policies are
// system-managed by Azure and created automatically with the account.
// They cannot be created or updated via Bicep/ARM templates.

// ── Outputs ──
@description('The resource name of the AI Services account')
output accountName string = aiServicesAccount.name

@description('The resource ID of the AI Services account')
output accountId string = aiServicesAccount.id

@description('The resource name of the Foundry project')
output projectName string = foundryProject.name

@description('The resource ID of the Foundry project')
output projectId string = foundryProject.id
