targetScope = 'resourceGroup'

resource nsg_checkout 'Microsoft.Network/networkSecurityGroups@2024-05-01' = {
  name: 'nsg-checkout'
  location: 'westeurope'
  tags: { environment: 'prod' }
  properties: {  }
}

resource rt_checkout 'Microsoft.Network/routeTables@2024-05-01' = {
  name: 'rt-checkout'
  location: 'westeurope'
  tags: { environment: 'prod' }
  properties: { disableBgpRoutePropagation: false }
}

resource vnet_commerce 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: 'vnet-commerce'
  location: 'westeurope'
  tags: { environment: 'prod', 'cost-center': 'digital-sales' }
  properties: { addressSpace: { addressPrefixes: ['10.40.0.0/16'] } }
}

resource privatelink_blob_core_windows_net 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  #disable-next-line no-hardcoded-env-urls
  name: 'privatelink.blob.core.windows.net'
  tags: { environment: 'prod' }
  properties: {  }
}

resource law_commerce_prod 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'law-commerce-prod'
  location: 'westeurope'
  tags: { environment: 'prod' }
  properties: { retentionInDays: 30, sku: { name: 'PerGB2018' } }
}

resource stcommerceprod01 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stcommerceprod01'
  location: 'westeurope'
  tags: { environment: 'prod', 'data-class': 'confidential' }
  kind: 'StorageV2'
  sku: { name: 'Standard_ZRS' }
  properties: {  }
}
