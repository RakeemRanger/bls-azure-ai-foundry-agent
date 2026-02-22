// ──────────────────────────────────────────────
// Private Endpoints for internal-only access
// ──────────────────────────────────────────────

@description('Private endpoint name')
param privateEndpointName string

@description('Resource ID of the service to connect to')
param serviceResourceId string

@description('Service type: "functionApp", "blob", "queue", "table", "file"')
param serviceType string

@description('Subnet resource ID where the private endpoint will be created')
param subnetId string

@description('VNet resource ID for DNS zone')
param vnetId string

@description('Deployment location')
param location string = resourceGroup().location

// Map service types to their group IDs and DNS zones
var serviceConfig = {
  functionApp: {
    groupId: 'sites'
    dnsZone: 'privatelink.azurewebsites.net'
  }
  functionAppScm: {
    groupId: 'sites'
    dnsZone: 'scm.privatelink.azurewebsites.net'
  }
  blob: {
    groupId: 'blob'
    dnsZone: 'privatelink.blob.${environment().suffixes.storage}'
  }
  queue: {
    groupId: 'queue'
    dnsZone: 'privatelink.queue.${environment().suffixes.storage}'
  }
}

var config = serviceConfig[serviceType]

// ── Private Endpoint ──
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: privateEndpointName
  location: location
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${privateEndpointName}-connection'
        properties: {
          privateLinkServiceId: serviceResourceId
          groupIds: [
            config.groupId
          ]
        }
      }
    ]
  }
}

// ── Private DNS Zone Link ──
resource dnzZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: config.dnsZone
  location: 'global'
  properties: {}
}

resource dnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: dnzZone
  name: '${privateEndpointName}-link'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetId
    }
  }
}

// ── DNS A Record ──
resource dnsRecord 'Microsoft.Network/privateDnsZones/A@2020-06-01' = {
  parent: dnzZone
  name: split(serviceResourceId, '/')[8] // Extract name from resource ID
  properties: {
    aRecords: [
      {
        ipv4Address: privateEndpoint.properties.customDnsConfigs[0].ipAddresses[0]
      }
    ]
    ttl: 3600
  }
}

// ── Outputs ──
@description('Private Endpoint resource ID')
output privateEndpointId string = privateEndpoint.id

@description('Private Endpoint network interface')
output networkInterfaceId string = privateEndpoint.properties.networkInterfaces[0].id

@description('Private IP address')
output privateIpAddress string = privateEndpoint.properties.customDnsConfigs[0].ipAddresses[0]

@description('DNS zone ID')
output dnsZoneId string = dnzZone.id
