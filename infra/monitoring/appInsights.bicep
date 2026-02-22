// ──────────────────────────────────────────────
// Application Insights for Function App Monitoring
// ──────────────────────────────────────────────

@description('Name of the Application Insights resource')
param appInsightsName string

@description('Deployment location')
param location string = resourceGroup().location

@description('Name of the Log Analytics workspace')
param workspaceName string

// ── Log Analytics Workspace ──
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// ── Application Insights ──
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ── Outputs ──
@description('The resource ID of Application Insights')
output appInsightsId string = appInsights.id

@description('The instrumentation key of Application Insights')
output instrumentationKey string = appInsights.properties.InstrumentationKey

@description('The connection string of Application Insights')
output connectionString string = appInsights.properties.ConnectionString

@description('The resource ID of the Log Analytics workspace')
output workspaceId string = logAnalyticsWorkspace.id
