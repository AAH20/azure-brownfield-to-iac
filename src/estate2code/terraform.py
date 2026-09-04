from __future__ import annotations

import json
from typing import Any

from .models import AzureResource, Ownership
from .support import safe_symbol, terraform_type


def _q(value: Any) -> str:
    return json.dumps(value)


def _tags(tags: dict[str, str]) -> list[str]:
    if not tags:
        return []
    lines = ["  tags = {"]
    lines.extend(f"    {_q(key)} = {_q(value)}" for key, value in sorted(tags.items()))
    lines.append("  }")
    return lines


def _body(resource: AzureResource) -> tuple[list[str], list[str]]:
    properties = resource.properties
    kind = resource.type.lower()
    preserved = ["name", "location", "tags"]
    if kind == "microsoft.resources/resourcegroups":
        return [f"  name     = {_q(resource.name)}", f"  location = {_q(resource.location)}", *_tags(resource.tags)], preserved
    common = [
        f"  name                = {_q(resource.name)}",
        f"  location            = {_q(resource.location)}",
        f"  resource_group_name = {_q(resource.resource_group)}",
    ]
    if kind == "microsoft.network/virtualnetworks":
        prefixes = properties.get("addressSpace", {}).get("addressPrefixes", [])
        preserved.append("properties.addressSpace.addressPrefixes")
        return [*common, f"  address_space = {_q(prefixes)}", *_tags(resource.tags)], preserved
    if kind == "microsoft.network/networksecuritygroups":
        return [*common, *_tags(resource.tags)], preserved
    if kind == "microsoft.network/routetables":
        disable = bool(properties.get("disableBgpRoutePropagation", False))
        preserved.append("properties.disableBgpRoutePropagation")
        return [*common, f"  bgp_route_propagation_enabled = {str(not disable).lower()}", *_tags(resource.tags)], preserved
    if kind == "microsoft.network/privatednszones":
        common.pop(1)
        return [*common, *_tags(resource.tags)], ["name", "tags"]
    if kind == "microsoft.storage/storageaccounts":
        sku = str(properties.get("sku", resource.properties.get("accountSku", "Standard_LRS")))
        if isinstance(properties.get("sku"), dict):
            sku = properties["sku"].get("name", "Standard_LRS")
        parts = sku.split("_", 1)
        preserved.append("properties.sku")
        return [*common, f"  account_tier             = {_q(parts[0])}",
                f"  account_replication_type = {_q(parts[1] if len(parts) > 1 else 'LRS')}", *_tags(resource.tags)], preserved
    if kind == "microsoft.operationalinsights/workspaces":
        sku = properties.get("sku", {}).get("name", "PerGB2018")
        retention = int(properties.get("retentionInDays", 30))
        preserved.extend(["properties.sku.name", "properties.retentionInDays"])
        return [*common, f"  sku               = {_q(sku)}", f"  retention_in_days = {retention}", *_tags(resource.tags)], preserved
    return [], []


def generate(resources: list[AzureResource], ownership: list[Ownership]) -> tuple[str, str, list[dict[str, Any]]]:
    ownership_by_id = {item.resource_id.lower(): item for item in ownership}
    blocks = [
        "terraform {",
        "  required_version = \">= 1.5.0\"",
        "  required_providers {",
        "    azurerm = { source = \"hashicorp/azurerm\", version = \">= 4.0, < 5.0\" }",
        "  }",
        "}",
        "",
        "provider \"azurerm\" { features {} }",
        "",
    ]
    imports: list[str] = []
    coverage: list[dict[str, Any]] = []
    used: dict[str, int] = {}
    for resource in resources:
        tf_type = terraform_type(resource.type)
        if not tf_type:
            coverage.append({"resource_id": resource.id, "status": "unsupported", "preserved": [], "manual_review": ["all properties"]})
            continue
        base = safe_symbol(resource.name)
        used[base] = used.get(base, 0) + 1
        symbol = base if used[base] == 1 else f"{base}_{used[base]}"
        body, preserved = _body(resource)
        blocks.extend([f"resource \"{tf_type}\" \"{symbol}\" {{", *body,
                       "  lifecycle { prevent_destroy = true }", "}", ""])
        owner = ownership_by_id[resource.id.lower()]
        if owner.status == "unmanaged":
            imports.extend(["import {", f"  to = {tf_type}.{symbol}", f"  id = {_q(resource.id)}", "}", ""])
        coverage.append({
            "resource_id": resource.id,
            "status": "scaffolded" if owner.status == "unmanaged" else "already-managed",
            "target": f"{tf_type}.{symbol}",
            "preserved": preserved,
            "manual_review": ["properties not explicitly listed as preserved", "provider defaults", "sensitive values"],
        })
    return "\n".join(blocks), "\n".join(imports), coverage
