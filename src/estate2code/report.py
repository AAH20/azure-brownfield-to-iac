from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from .models import AzureResource, Ownership


def build_report(resources: list[AzureResource], ownership: list[Ownership], order: list[AzureResource],
                 warnings: list[str], terraform_coverage: list[dict[str, Any]],
                 bicep_coverage: list[dict[str, Any]]) -> dict[str, Any]:
    supported = sum(item["status"] != "unsupported" for item in terraform_coverage)
    report = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "simulated",
        "summary": {
            "resources": len(resources),
            "managed": sum(item.status == "managed" for item in ownership),
            "unmanaged": sum(item.status == "unmanaged" for item in ownership),
            "terraform_supported": supported,
            "terraform_coverage_percent": round(100 * supported / len(resources), 2) if resources else 0,
            "warnings": len(warnings),
        },
        "ownership": [item.to_dict() for item in ownership],
        "dependency_order": [resource.id for resource in order],
        "warnings": warnings,
        "terraform_coverage": terraform_coverage,
        "bicep_coverage": bicep_coverage,
        "claim_boundary": "Generated code is an adoption scaffold; compilation or import does not prove semantic equivalence or production safety.",
    }
    stable = json.dumps({key: value for key, value in report.items() if key != "generated_at"}, sort_keys=True, separators=(",", ":")).encode()
    report["receipt"] = {"algorithm": "sha256", "content_digest": hashlib.sha256(stable).hexdigest()}
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Estate2Code adoption report", "",
        "## Inventory", "",
        f"- Resources: {summary['resources']}",
        f"- Already managed: {summary['managed']}",
        f"- Unmanaged: {summary['unmanaged']}",
        f"- Terraform scaffold coverage: {summary['terraform_coverage_percent']}%", "",
        "## Dependency-safe import order", "",
    ]
    lines.extend(f"{index}. `{resource_id}`" for index, resource_id in enumerate(report["dependency_order"], 1))
    lines.extend(["", "## Manual review and unsupported resources", ""])
    unsupported = [item for item in report["terraform_coverage"] if item["status"] == "unsupported"]
    lines.extend(f"- Unsupported: `{item['resource_id']}`" for item in unsupported)
    lines.extend(f"- Warning: {warning}" for warning in report["warnings"])
    if not unsupported and not report["warnings"]:
        lines.append("- No inventory-level exceptions; property-level review remains required.")
    lines.extend(["", f"> {report['claim_boundary']}", ""])
    return "\n".join(lines)
