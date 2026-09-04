#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python3 -m unittest discover -s tests -v

output_dir="${TMPDIR:-/tmp}/estate2code-validation"
rm -rf "$output_dir"
PYTHONPATH=src python3 -m estate2code.cli \
  examples/resource-graph-estate.json \
  --format resource-graph \
  --terraform-state examples/terraform-state.json \
  --output "$output_dir"

test -s "$output_dir/terraform/main.tf"
test -s "$output_dir/terraform/imports.tf"
test -s "$output_dir/bicep/rg_commerce_prod.bicep"
test -s "$output_dir/adoption-report.json"

grep -q 'prevent_destroy = true' "$output_dir/terraform/main.tf"
grep -q 'Microsoft.KeyVault' "$output_dir/adoption-report.md"
