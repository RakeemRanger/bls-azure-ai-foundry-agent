targetScope = 'subscription'

@allowed([
  'dev'
  'prod'
  'sweden'
])
param environmentType string

@allowed([
  'canadaeast'
  'eastus'
  'westeurope'
  'swedencentral'
])
@metadata({
  azd: {
    type: 'location'
  }
})
param location string = 'swedencentral'

@description('GitHub repository URL for function app deployment (e.g., https://github.com/username/repo)')
param githubRepoUrl string = ''

@description('GitHub branch to deploy from')
param githubBranch string = 'main'

@description('Enable automatic deployment from GitHub')
param enableGitHubDeploy bool = false

// ── Naming ──
var resourceNamePrefix = 'ranger-bls'
var resourceGroupName = '${resourceNamePrefix}-${environmentType}-rg'
var accountName = '${resourceNamePrefix}-${environmentType}-ai'
var identityName = '${resourceNamePrefix}-${environmentType}-msi'
var projectName = 'dbot'
var storageAccountName = '${replace(resourceNamePrefix, '-', '')}${environmentType}func'
var agentStorageAccountName = '${replace(resourceNamePrefix, '-', '')}${environmentType}agent'
var functionAppName = '${resourceNamePrefix}-${environmentType}-func'
var appServicePlanName = '${resourceNamePrefix}-${environmentType}-asp'
var appInsightsName = '${resourceNamePrefix}-${environmentType}-ai-insights'
var workspaceName = '${resourceNamePrefix}-${environmentType}-log'

// ── Queue Names ──
var agentCreationQueueName = 'agent-creation-queue'
var skAgentRequestQueueName = 'sk-agent-request-queue'
var skAgentResponseQueueName = 'sk-agent-response-queue'
var queueNames = [agentCreationQueueName, skAgentRequestQueueName, skAgentResponseQueueName]

// ── Agent definitions — add new agents here ──
var agents = [
  {
    name: 'dartinbot'
    mcpEndpoint: 'https://dbot-mcp-func-premium.azurewebsites.net/runtime/webhooks/mcp'
    models: [
      {
        name: 'gpt-4.1'
        skuName: 'GlobalStandard'
        capacity: 50
        format: 'OpenAI'
        modelName: 'gpt-4.1'
        version: '2025-04-14'
      }
      // Note: text-embedding-3-small with Standard SKU not available in swedencentral
      // Uncomment and adjust SKU if needed for your region
      // {
      //   name: 'text-embedding-3-small'
      //   skuName: 'Standard'
      //   capacity: 120
      //   format: 'OpenAI'
      //   modelName: 'text-embedding-3-small'
      //   version: '1'
      // }
    ]
  }
  // Add more agents here:
  // {
  //   name: 'another-agent'
  //   mcpEndpoint: 'https://another-func.azurewebsites.net/runtime/webhooks/mcp'
  //   models: [ ... ]
  // }
]

// ── Resource Group ──
resource rg 'Microsoft.Resources/resourceGroups@2025-04-01' = {
  name: resourceGroupName
  location: location
}

// ── 1. Managed Identity ──
module identity 'identity/msi.bicep' = {
  name: 'identity-deployment'
  scope: rg
  params: {
    identityName: identityName
    location: location
  }
}

// ── 2. AI Foundry Account + Project ──
module foundryAccount 'foundryAccount/foundry_account.bicep' = {
  name: 'foundry-account-deployment'
  scope: rg
  params: {
    accountName: accountName
    location: location
    userAssignedIdentityId: identity.outputs.identityId
    projectName: projectName
  }
}

// ── 3. Agent Deployments (one per agent) ──
module agent 'agent/agent.bicep' = [
  for (agentDef, i) in agents: {
    name: 'agent-${agentDef.name}-deployment'
    scope: rg
    params: {
      accountName: foundryAccount.outputs.accountName
      projectName: foundryAccount.outputs.projectName
      agentName: agentDef.name
      mcpEndpoint: agentDef.mcpEndpoint
      modelDeployments: agentDef.models
    }
  }
]

// ── 4. RBAC for Foundry Managed Identity ──
module rbac 'rbac/rbac.bicep' = {
  name: 'rbac-deployment'
  scope: rg
  params: {
    principalId: identity.outputs.principalId
    aiServicesAccountId: foundryAccount.outputs.accountId
    agentStorageAccountId: agentStorage.outputs.storageAccountId
  }
}

// ── 5. Storage Queue Connection for Foundry Project ──
module storageConnection 'connections/storageConnection.bicep' = {
  name: 'storage-connection-deployment'
  scope: rg
  params: {
    accountName: foundryAccount.outputs.accountName
    projectName: foundryAccount.outputs.projectName
    connectionName: 'agent-queue-storage'
    storageAccountId: agentStorage.outputs.storageAccountId
  }
  dependsOn: [
    rbac
  ]
}

// ── 6. Application Insights for Monitoring ──
module appInsights 'monitoring/appInsights.bicep' = {
  name: 'appinsights-deployment'
  scope: rg
  params: {
    appInsightsName: appInsightsName
    workspaceName: workspaceName
    location: location
  }
}

// ── 7. Storage Account for Function App Backend ──
module functionStorage 'storage/storage.bicep' = {
  name: 'function-storage-deployment'
  scope: rg
  params: {
    storageAccountName: storageAccountName
    location: location
    queueNames: ['function-backend-queue']
  }
}

// ── 8. Storage Account for Agent Queues (Private)──
module agentStorage 'storage/storage.bicep' = {
  name: 'agent-storage-deployment'
  scope: rg
  params: {
    storageAccountName: agentStorageAccountName
    location: location
    queueNames: queueNames // agent-creation, sk-agent-request, sk-agent-response
  }
}

// ── 9. App Service Plan ──
module appServicePlan 'appServicePlan/appServicePlan.bicep' = {
  name: 'app-service-plan-deployment'
  scope: rg
  params: {
    appServicePlanName: appServicePlanName
    location: location
    skuName: 'Y1' // Consumption plan
    isElasticPremium: false
  }
}

// ── 10. Function App ──
module functionApp 'functionApp/functionApp.bicep' = {
  name: 'function-app-deployment'
  scope: rg
  params: {
    functionAppName: functionAppName
    location: location
    appServicePlanId: appServicePlan.outputs.appServicePlanId
    storageAccountName: functionStorage.outputs.storageAccountName
    agentStorageAccountName: agentStorage.outputs.storageAccountName
    agentCreationQueueName: agentCreationQueueName
    skAgentRequestQueueName: skAgentRequestQueueName
    skAgentResponseQueueName: skAgentResponseQueueName
    userAssignedIdentityId: identity.outputs.identityId
    aiServicesEndpoint: 'https://${foundryAccount.outputs.accountName}.cognitiveservices.azure.com/'
    aiServicesAccountName: foundryAccount.outputs.accountName
    projectName: foundryAccount.outputs.projectName
    allowPublicAccess: false // Internal-only Function App
    appInsightsConnectionString: appInsights.outputs.connectionString
    // GitHub deployment parameters (not used - deploy via GitHub Actions instead)
    githubRepoUrl: ''
    githubBranch: ''
    enableGitHubDeploy: false
  }
}

// ── 11. RBAC for Function App ──
module functionAppRbac 'rbac/functionAppRbac.bicep' = {
  name: 'function-app-rbac-deployment'
  scope: rg
  params: {
    functionAppPrincipalId: identity.outputs.principalId
    functionStorageAccountId: functionStorage.outputs.storageAccountId
    agentStorageAccountId: agentStorage.outputs.storageAccountId
    aiServicesAccountId: foundryAccount.outputs.accountId
  }
  dependsOn: [
    functionApp
  ]
}

// ── Outputs ──
output resourceGroupName string = rg.name
output accountName string = foundryAccount.outputs.accountName
output projectName string = foundryAccount.outputs.projectName
output identityClientId string = identity.outputs.clientId
output functionAppName string = functionApp.outputs.functionAppName
output functionAppHostName string = functionApp.outputs.functionAppHostName
output agentStorageAccountName string = agentStorage.outputs.storageAccountName
output agentCreationQueueName string = agentCreationQueueName
output skAgentRequestQueueName string = skAgentRequestQueueName
output skAgentResponseQueueName string = skAgentResponseQueueName
output storageConnectionName string = storageConnection.outputs.connectionName
output queueEndpoint string = storageConnection.outputs.queueEndpoint
output appInsightsName string = appInsightsName
output appInsightsConnectionString string = appInsights.outputs.connectionString
