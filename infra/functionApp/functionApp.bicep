// ──────────────────────────────────────────────
// Function App for Agent Creation Queue Processing
// Internal-only with managed identity
// ──────────────────────────────────────────────

@description('Name of the Function App')
param functionAppName string

@description('Deployment location')
param location string = resourceGroup().location

@description('Resource ID of the App Service Plan')
param appServicePlanId string

@description('Name of the storage account for function app backend')
param storageAccountName string

@description('Name of the storage account for agent queue processing')
param agentStorageAccountName string

@description('Name of the agent creation queue')
param agentCreationQueueName string

@description('Name of the SK agent request queue')
param skAgentRequestQueueName string

@description('Name of the SK agent response queue')
param skAgentResponseQueueName string

@description('Resource ID of the user-assigned managed identity')
param userAssignedIdentityId string

@description('AI Services account endpoint for agent creation')
param aiServicesEndpoint string

@description('AI Services account name')
param aiServicesAccountName string

@description('Foundry project name')
param projectName string

@description('Enable public network access')
param allowPublicAccess bool = false

@description('Application Insights connection string')
param appInsightsConnectionString string = ''

@description('GitHub repository URL for source control deployment')
param githubRepoUrl string = ''

@description('GitHub repository branch')
param githubBranch string = 'main'

@description('Enable GitHub source control deployment')
param enableGitHubDeploy bool = false

// ── Function App ──
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlanId
    reserved: true
    publicNetworkAccess: allowPublicAccess ? 'Enabled' : 'Disabled'
    httpsOnly: true
    keyVaultReferenceIdentity: userAssignedIdentityId
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage__accountName'
          value: storageAccountName
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AGENT_STORAGE_ACCOUNT__queueServiceUri'
          value: 'https://${agentStorageAccountName}.queue.${environment().suffixes.storage}'
        }
        {
          name: 'AGENT_CREATION_QUEUE_NAME'
          value: agentCreationQueueName
        }
        {
          name: 'SK_AGENT_REQUEST_QUEUE_NAME'
          value: skAgentRequestQueueName
        }
        {
          name: 'SK_AGENT_RESPONSE_QUEUE_NAME'
          value: skAgentResponseQueueName
        }
        {
          name: 'AI_SERVICES_ENDPOINT'
          value: aiServicesEndpoint
        }
        {
          name: 'AI_SERVICES_ACCOUNT_NAME'
          value: aiServicesAccountName
        }
        {
          name: 'FOUNDRY_PROJECT_NAME'
          value: projectName
        }
        {
          name: 'AZURE_CLIENT_ID'
          value: reference(userAssignedIdentityId, '2023-01-31').clientId
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
      ]
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      alwaysOn: false
      cors: {
        allowedOrigins: []
      }
    }
  }
}

// ── GitHub Source Control Deployment ──
resource sourceControl 'Microsoft.Web/sites/sourcecontrols@2023-01-01' = if (enableGitHubDeploy && !empty(githubRepoUrl)) {
  parent: functionApp
  name: 'web'
  properties: {
    repoUrl: githubRepoUrl
    branch: githubBranch
    isManualIntegration: true
    deploymentRollbackEnabled: false
    isMercurial: false
  }
}

// ── Outputs ──
@description('The resource ID of the Function App')
output functionAppId string = functionApp.id

@description('The resource name of the Function App')
output functionAppName string = functionApp.name

@description('The default hostname of the Function App')
output functionAppHostName string = functionApp.properties.defaultHostName

@description('The principal ID of the Function App managed identity')
output functionAppPrincipalId string = reference(userAssignedIdentityId, '2023-01-31').principalId
