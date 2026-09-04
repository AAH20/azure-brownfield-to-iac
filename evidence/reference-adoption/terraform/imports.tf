import {
  to = azurerm_resource_group.rg_commerce_prod
  id = "/subscriptions/demo/resourceGroups/rg-commerce-prod"
}

import {
  to = azurerm_network_security_group.nsg_checkout
  id = "/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-checkout"
}

import {
  to = azurerm_route_table.rt_checkout
  id = "/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Network/routeTables/rt-checkout"
}

import {
  to = azurerm_virtual_network.vnet_commerce
  id = "/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Network/virtualNetworks/vnet-commerce"
}

import {
  to = azurerm_private_dns_zone.privatelink_blob_core_windows_net
  id = "/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net"
}

import {
  to = azurerm_storage_account.stcommerceprod01
  id = "/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Storage/storageAccounts/stcommerceprod01"
}
