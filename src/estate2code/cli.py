from __future__ import annotations

import argparse
import json

from .compiler import compile_estate, write_files
from .normalize import load_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile an Azure brownfield inventory into reviewable IaC adoption scaffolds")
    parser.add_argument("inventory")
    parser.add_argument("--format", choices=["resource-graph", "arm", "canonical"], required=True)
    parser.add_argument("--terraform-state")
    parser.add_argument("--output", default="generated/estate2code")
    args = parser.parse_args()
    state = load_json(args.terraform_state) if args.terraform_state else None
    files, report = compile_estate(load_json(args.inventory), args.format, state)
    written = write_files(files, args.output)
    print(json.dumps({"summary": report["summary"], "files": [str(path) for path in written]}, indent=2))


if __name__ == "__main__":
    main()
