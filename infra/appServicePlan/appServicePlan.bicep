// ──────────────────────────────────────────────
// App Service Plan for Function App
// ──────────────────────────────────────────────

@description('Name of the App Service Plan')
param appServicePlanName string

@description('Deployment location')
param location string = resourceGroup().location

@description('SKU for the App Service Plan')
@allowed([
  'Y1'  // Consumption
  'EP1' // Elastic Premium
  'EP2'
  'EP3'
])
param skuName string = 'Y1'

@description('Whether to use Elastic Premium for VNet integration')
param isElasticPremium bool = false

// ── App Service Plan ──
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: skuName
    tier: isElasticPremium ? 'ElasticPremium' : 'Dynamic'
  }
  kind: isElasticPremium ? 'elastic' : 'functionapp'
  properties: {
    reserved: true // Linux
  }
}

// ── Outputs ──
@description('The resource ID of the App Service Plan')
output appServicePlanId string = appServicePlan.id

@description('The resource name of the App Service Plan')
output appServicePlanName string = appServicePlan.name
