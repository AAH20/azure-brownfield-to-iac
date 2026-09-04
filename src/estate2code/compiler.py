from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bicep import generate as generate_bicep
from .graph import dependency_order
from .normalize import normalize
from .ownership import classify
from .report import build_report, markdown
from .terraform import generate as generate_terraform


def compile_estate(inventory: Any, input_format: str, terraform_state: dict[str, Any] | None = None) -> tuple[dict[str, str], dict[str, Any]]:
    resources = normalize(inventory, input_format)
    ordered, warnings = dependency_order(resources)
    ownership = classify(resources, terraform_state)
    terraform_main, imports, tf_coverage = generate_terraform(ordered, ownership)
    bicep_files, bicep_coverage = generate_bicep(ordered)
    report = build_report(resources, ownership, ordered, warnings, tf_coverage, bicep_coverage)
    files = {"terraform/main.tf": terraform_main, "terraform/imports.tf": imports, **bicep_files}
    files["adoption-report.json"] = json.dumps(report, indent=2) + "\n"
    files["adoption-report.md"] = markdown(report)
    files["impactgraph/canonical-changes.json"] = json.dumps({"changes": []}, indent=2) + "\n"
    return files, report


def write_files(files: dict[str, str], output_dir: str | Path) -> list[Path]:
    root = Path(output_dir)
    written: list[Path] = []
    for relative_path, content in files.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written
