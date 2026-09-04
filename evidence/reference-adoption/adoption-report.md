# Estate2Code adoption report

## Inventory

- Resources: 8
- Already managed: 1
- Unmanaged: 7
- Terraform scaffold coverage: 87.5%

## Dependency-safe import order

1. `/subscriptions/demo/resourceGroups/rg-commerce-prod`
2. `/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.KeyVault/vaults/kv-commerce-prod`
3. `/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-checkout`
4. `/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Network/routeTables/rt-checkout`
5. `/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Network/virtualNetworks/vnet-commerce`
6. `/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net`
7. `/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.OperationalInsights/workspaces/law-commerce-prod`
8. `/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.Storage/storageAccounts/stcommerceprod01`

## Manual review and unsupported resources

- Unsupported: `/subscriptions/demo/resourceGroups/rg-commerce-prod/providers/Microsoft.KeyVault/vaults/kv-commerce-prod`

> Generated code is an adoption scaffold; compilation or import does not prove semantic equivalence or production safety.
