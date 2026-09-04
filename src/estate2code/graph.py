from __future__ import annotations

from collections import defaultdict

from .models import AzureResource


def dependency_order(resources: list[AzureResource]) -> tuple[list[AzureResource], list[str]]:
    by_id = {resource.id.lower(): resource for resource in resources}
    inbound = {resource_id: 0 for resource_id in by_id}
    outgoing: dict[str, set[str]] = defaultdict(set)
    warnings: list[str] = []
    for resource_id, resource in by_id.items():
        for dependency in resource.depends_on:
            dep_id = dependency.lower()
            if dep_id not in by_id:
                warnings.append(f"{resource.id} references inventory-external dependency {dependency}")
                continue
            if resource_id not in outgoing[dep_id]:
                outgoing[dep_id].add(resource_id)
                inbound[resource_id] += 1
    ready = sorted(resource_id for resource_id, count in inbound.items() if count == 0)
    ordered: list[AzureResource] = []
    while ready:
        current = ready.pop(0)
        ordered.append(by_id[current])
        for dependent in sorted(outgoing.get(current, set())):
            inbound[dependent] -= 1
            if inbound[dependent] == 0:
                ready.append(dependent)
                ready.sort()
    if len(ordered) != len(resources):
        cyclic = sorted(resource_id for resource_id, count in inbound.items() if count > 0)
        raise ValueError(f"dependency cycle detected: {', '.join(cyclic)}")
    return ordered, warnings
