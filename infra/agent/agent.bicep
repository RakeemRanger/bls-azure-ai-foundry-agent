// ──────────────────────────────────────────────
// Dynamic Agent Module
// Deploy once per agent — creates model deployments,
// account-level connection, and project-level connection.
// ──────────────────────────────────────────────

@description('Name of the existing AI Services account')
param accountName string

@description('Name of the existing Foundry project')
param projectName string

@description('Unique name for this agent (used for connections)')
param agentName string

@description('MCP endpoint URL for the agent remote tool')
param mcpEndpoint string

@description('Model deployments for this agent')
param modelDeployments array

@description('RAI policy to apply to model deployments')
param raiPolicyName string = 'Microsoft.DefaultV2'

// ── Reference existing account & project ──
resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: accountName
}

resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' existing = {
  parent: aiServicesAccount
  name: projectName
}

// ── Model Deployments ──
@batchSize(1)
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = [
  for model in modelDeployments: {
    parent: aiServicesAccount
    name: model.name
    sku: {
      name: model.skuName
      capacity: model.capacity
    }
    properties: {
      model: {
        format: model.format
        name: model.modelName
        version: model.version
      }
      versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
      currentCapacity: model.capacity
      raiPolicyName: raiPolicyName
    }
  }
]

// ── Account-level MCP Tool Connection ──
resource accountConnection 'Microsoft.CognitiveServices/accounts/connections@2025-06-01' = {
  parent: aiServicesAccount
  name: agentName
  properties: {
    authType: 'OAuth2'
    category: 'RemoteTool'
    target: mcpEndpoint
    useWorkspaceManagedIdentity: false
    isSharedToAll: false
    sharedUserList: []
    peRequirement: 'NotRequired'
    peStatus: 'NotApplicable'
    credentials: {
      clientId: '00000000-0000-0000-0000-000000000000'
      clientSecret: 'bogus-secret-for-testing'
      tenantId: '00000000-0000-0000-0000-000000000000'
      authUrl: '${environment().authentication.loginEndpoint}00000000-0000-0000-0000-000000000000'
    }
    metadata: {
      ApiType: 'Azure'
    }
  }
}

// ── Project-level MCP Tool Connection ──
resource projectConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-06-01' = {
  parent: foundryProject
  name: agentName
  properties: {
    authType: 'OAuth2'
    category: 'RemoteTool'
    target: mcpEndpoint
    useWorkspaceManagedIdentity: false
    isSharedToAll: false
    sharedUserList: []
    peRequirement: 'NotRequired'
    peStatus: 'NotApplicable'
    credentials: {
      clientId: '00000000-0000-0000-0000-000000000000'
      clientSecret: 'bogus-secret-for-testing'
      tenantId: '00000000-0000-0000-0000-000000000000'
      authUrl: '${environment().authentication.loginEndpoint}00000000-0000-0000-0000-000000000000'
    }
    metadata: {
      ApiType: 'Azure'
    }
  }
  dependsOn: [
    aiServicesAccount
  ]
}

// ── Outputs ──
output agentName string = agentName
output accountConnectionName string = accountConnection.name
output projectConnectionName string = projectConnection.name
output deployedModels array = [
  for (model, i) in modelDeployments: {
    name: modelDeployment[i].name
    id: modelDeployment[i].id
  }
]
