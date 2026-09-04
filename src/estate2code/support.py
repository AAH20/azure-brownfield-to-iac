from __future__ import annotations


SUPPORTED = {
    "microsoft.resources/resourcegroups": "azurerm_resource_group",
    "microsoft.network/virtualnetworks": "azurerm_virtual_network",
    "microsoft.network/networksecuritygroups": "azurerm_network_security_group",
    "microsoft.network/routetables": "azurerm_route_table",
    "microsoft.network/privatednszones": "azurerm_private_dns_zone",
    "microsoft.storage/storageaccounts": "azurerm_storage_account",
    "microsoft.operationalinsights/workspaces": "azurerm_log_analytics_workspace",
}


def terraform_type(azure_type: str) -> str | None:
    return SUPPORTED.get(azure_type.lower())


def safe_symbol(value: str) -> str:
    cleaned = "".join(character if character.isalnum() else "_" for character in value.lower()).strip("_")
    if not cleaned or cleaned[0].isdigit():
        cleaned = f"resource_{cleaned}"
    return cleaned
