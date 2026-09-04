from __future__ import annotations

from typing import Any

from .models import AzureResource, Ownership


def terraform_resource_ids(state: dict[str, Any] | None) -> dict[str, str]:
    found: dict[str, str] = {}
    if not state:
        return found
    for resource in state.get("resources", []):
        module = resource.get("module")
        base = f"{module}." if module else ""
        base += f"{resource.get('type')}.{resource.get('name')}"
        for index, instance in enumerate(resource.get("instances", [])):
            resource_id = (instance.get("attributes") or {}).get("id")
            if resource_id:
                suffix = f"[{index}]" if len(resource.get("instances", [])) > 1 else ""
                found[str(resource_id).lower()] = f"{base}{suffix}"
    return found


def classify(resources: list[AzureResource], state: dict[str, Any] | None) -> list[Ownership]:
    managed = terraform_resource_ids(state)
    return [Ownership(
        resource_id=resource.id,
        status="managed" if resource.id.lower() in managed else "unmanaged",
        terraform_address=managed.get(resource.id.lower()),
    ) for resource in resources]
