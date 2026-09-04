from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class AzureResource:
    id: str
    name: str
    type: str
    resource_group: str
    location: str
    tags: dict[str, str] = field(default_factory=dict)
    properties: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["depends_on"] = list(self.depends_on)
        return value


@dataclass(frozen=True)
class Ownership:
    resource_id: str
    status: str
    terraform_address: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
