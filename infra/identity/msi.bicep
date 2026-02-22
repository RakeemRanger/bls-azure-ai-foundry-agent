// ──────────────────────────────────────────────
// User-Assigned Managed Identity
// ──────────────────────────────────────────────

@description('Name of the managed identity')
param identityName string

@description('Deployment location')
param location string = resourceGroup().location

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

// ── Outputs ──
@description('The resource ID of the managed identity')
output identityId string = managedIdentity.id

@description('The principal ID (object ID) of the managed identity')
output principalId string = managedIdentity.properties.principalId

@description('The client ID of the managed identity')
output clientId string = managedIdentity.properties.clientId

