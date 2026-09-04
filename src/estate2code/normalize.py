from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import AzureResource


def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def resource_group_from_id(resource_id: str) -> str:
    match = re.search(r"/resourceGroups/([^/]+)", resource_id, re.IGNORECASE)
    return match.group(1) if match else ""


def _dependencies(item: dict[str, Any]) -> tuple[str, ...]:
    explicit = item.get("dependsOn", item.get("depends_on", []))
    properties = item.get("properties") or {}
    inferred: list[str] = []
    for key in ("virtualNetwork", "subnet", "networkSecurityGroup", "routeTable", "privateLinkServiceConnectionState"):
        value = properties.get(key)
        if isinstance(value, dict) and isinstance(value.get("id"), str):
            inferred.append(value["id"])
    return tuple(dict.fromkeys([*explicit, *inferred]))


def normalize_item(item: dict[str, Any]) -> AzureResource:
    resource_id = item["id"]
    properties = dict(item.get("properties") or {})
    for key in ("kind", "sku"):
        if key in item and key not in properties:
            properties[key] = item[key]
    return AzureResource(
        id=resource_id,
        name=item.get("name", resource_id.rstrip("/").split("/")[-1]),
        type=item["type"],
        resource_group=item.get("resourceGroup", resource_group_from_id(resource_id)),
        location=item.get("location", "global"),
        tags={str(k): str(v) for k, v in (item.get("tags") or {}).items()},
        properties=properties,
        depends_on=_dependencies(item),
    )


def normalize(document: Any, input_format: str) -> list[AzureResource]:
    if input_format == "resource-graph":
        items = document.get("data", document) if isinstance(document, dict) else document
    elif input_format == "arm":
        items = document.get("resources", [])
    else:
        items = document.get("resources", document) if isinstance(document, dict) else document
    resources = [normalize_item(item) for item in items]
    ids = [resource.id.lower() for resource in resources]
    if len(ids) != len(set(ids)):
        raise ValueError("inventory contains duplicate resource identifiers")
    return resources
