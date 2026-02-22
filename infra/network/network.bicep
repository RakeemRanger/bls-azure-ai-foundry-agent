// ──────────────────────────────────────────────
// Virtual Network and Private Endpoints
// ──────────────────────────────────────────────

@description('Virtual Network name')
param vnetName string

@description('Virtual Network address space')
param vnetAddressSpace string = '10.0.0.0/16'

@description('Subnet address space')
param subnetAddressSpace string = '10.0.1.0/24'

@description('Deployment location')
param location string = resourceGroup().location

// ── Virtual Network ──
resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressSpace
      ]
    }
    subnets: [
      {
        name: 'default'
        properties: {
          addressPrefix: subnetAddressSpace
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
    ]
  }
}

// ── Outputs ──
@description('Virtual Network resource ID')
output vnetId string = vnet.id

@description('Virtual Network name')
output vnetName string = vnet.name

@description('Default subnet resource ID')
output subnetId string = vnet.properties.subnets[0].id

@description('Default subnet name')
output subnetName string = vnet.properties.subnets[0].name
