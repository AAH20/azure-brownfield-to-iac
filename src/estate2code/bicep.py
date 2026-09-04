from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from .models import AzureResource
from .support import safe_symbol, terraform_type


API_VERSIONS = {
    "microsoft.network/virtualnetworks": "2024-05-01",
    "microsoft.network/networksecuritygroups": "2024-05-01",
    "microsoft.network/routetables": "2024-05-01",
    "microsoft.network/privatednszones": "2024-06-01",
    "microsoft.storage/storageaccounts": "2023-05-01",
    "microsoft.operationalinsights/workspaces": "2023-09-01",
}


def _bicep(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    if isinstance(value, list):
        return "[" + ", ".join(_bicep(item) for item in value) + "]"
    if isinstance(value, dict):
        pairs = []
        for key, item in value.items():
            rendered_key = key if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) else _bicep(key)
            pairs.append(f"{rendered_key}: {_bicep(item)}")
        return "{ " + ", ".join(pairs) + " }"
    raise TypeError(f"unsupported Bicep literal type: {type(value).__name__}")


def _resource_block(resource: AzureResource, symbol: str) -> str:
    kind = resource.type.lower()
    version = API_VERSIONS[kind]
    lines = [f"resource {symbol} '{resource.type}@{version}' = {{"]
    if kind == "microsoft.network/privatednszones" and ".windows.net" in resource.name.lower():
        lines.append("  #disable-next-line no-hardcoded-env-urls")
    lines.append(f"  name: {_bicep(resource.name)}")
    if resource.location.lower() != "global":
        lines.append(f"  location: {_bicep(resource.location)}")
    if resource.tags:
        lines.append(f"  tags: {_bicep(resource.tags)}")
    properties: dict[str, Any] = {}
    if kind == "microsoft.network/virtualnetworks":
        properties["addressSpace"] = resource.properties.get("addressSpace", {"addressPrefixes": []})
    elif kind == "microsoft.network/routetables":
        properties["disableBgpRoutePropagation"] = bool(resource.properties.get("disableBgpRoutePropagation", False))
    elif kind == "microsoft.storage/storageaccounts":
        lines.append(f"  kind: {_bicep(resource.properties.get('kind', 'StorageV2'))}")
        sku = resource.properties.get("sku", {"name": "Standard_LRS"})
        if isinstance(sku, str):
            sku = {"name": sku}
        lines.append(f"  sku: {_bicep(sku)}")
    elif kind == "microsoft.operationalinsights/workspaces":
        properties["retentionInDays"] = int(resource.properties.get("retentionInDays", 30))
        properties["sku"] = resource.properties.get("sku", {"name": "PerGB2018"})
    lines.append(f"  properties: {_bicep(properties)}")
    lines.append("}")
    return "\n".join(lines)


def generate(resources: list[AzureResource]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    groups: dict[str, list[AzureResource]] = defaultdict(list)
    coverage: list[dict[str, Any]] = []
    for resource in resources:
        kind = resource.type.lower()
        if kind == "microsoft.resources/resourcegroups":
            coverage.append({"resource_id": resource.id, "status": "manifest-only", "reason": "resource-group scope boundary"})
        elif kind in API_VERSIONS and terraform_type(resource.type):
            groups[resource.resource_group].append(resource)
        else:
            coverage.append({"resource_id": resource.id, "status": "unsupported"})
    files: dict[str, str] = {}
    for group, members in sorted(groups.items()):
        used: dict[str, int] = {}
        blocks = ["targetScope = 'resourceGroup'", ""]
        for resource in members:
            base = safe_symbol(resource.name)
            used[base] = used.get(base, 0) + 1
            symbol = base if used[base] == 1 else f"{base}_{used[base]}"
            blocks.extend([_resource_block(resource, symbol), ""])
            coverage.append({"resource_id": resource.id, "status": "scaffolded", "file": f"bicep/{safe_symbol(group)}.bicep"})
        files[f"bicep/{safe_symbol(group)}.bicep"] = "\n".join(blocks)
    return files, coverage
