from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from estate2code.compiler import compile_estate, write_files
from estate2code.graph import dependency_order
from estate2code.normalize import load_json, normalize
from estate2code.ownership import classify


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = load_json(ROOT / "examples" / "resource-graph-estate.json")
STATE = load_json(ROOT / "examples" / "terraform-state.json")


class Estate2CodeTests(unittest.TestCase):
    def test_resource_graph_inventory_is_normalized(self):
        resources = normalize(INVENTORY, "resource-graph")
        self.assertEqual(len(resources), 8)
        self.assertEqual(resources[3].resource_group, "rg-commerce-prod")

    def test_resource_graph_top_level_sku_is_preserved(self):
        document = {"data": [{
            "id": "/subscriptions/demo/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/example",
            "name": "example",
            "type": "Microsoft.Storage/storageAccounts",
            "resourceGroup": "rg",
            "location": "eastus",
            "kind": "StorageV2",
            "sku": {"name": "Standard_GRS"},
        }]}
        resource = normalize(document, "resource-graph")[0]
        self.assertEqual(resource.properties["sku"]["name"], "Standard_GRS")
        self.assertEqual(resource.properties["kind"], "StorageV2")

    def test_dependency_order_places_resource_group_first(self):
        resources = normalize(INVENTORY, "resource-graph")
        ordered, warnings = dependency_order(resources)
        self.assertEqual(ordered[0].type.lower(), "microsoft.resources/resourcegroups")
        self.assertEqual(warnings, [])
        positions = {resource.id: index for index, resource in enumerate(ordered)}
        vnet = next(resource for resource in resources if resource.type.endswith("virtualNetworks"))
        for dependency in vnet.depends_on:
            self.assertLess(positions[dependency], positions[vnet.id])

    def test_state_classifies_one_resource_as_managed(self):
        resources = normalize(INVENTORY, "resource-graph")
        ownership = classify(resources, STATE)
        self.assertEqual(sum(item.status == "managed" for item in ownership), 1)
        managed = next(item for item in ownership if item.status == "managed")
        self.assertEqual(managed.terraform_address, "azurerm_log_analytics_workspace.existing")

    def test_compiler_generates_imports_only_for_unmanaged_supported_resources(self):
        files, report = compile_estate(INVENTORY, "resource-graph", STATE)
        imports = files["terraform/imports.tf"]
        self.assertIn("azurerm_virtual_network.vnet_commerce", imports)
        self.assertNotIn("azurerm_log_analytics_workspace.law_commerce_prod", imports)
        self.assertEqual(report["summary"]["managed"], 1)
        self.assertEqual(report["summary"]["terraform_supported"], 7)

    def test_unsupported_resource_is_explicit(self):
        _, report = compile_estate(INVENTORY, "resource-graph", STATE)
        unsupported = [item for item in report["terraform_coverage"] if item["status"] == "unsupported"]
        self.assertEqual(len(unsupported), 1)
        self.assertIn("Microsoft.KeyVault", unsupported[0]["resource_id"])

    def test_generated_terraform_has_safety_and_provider_constraints(self):
        files, _ = compile_estate(INVENTORY, "resource-graph", STATE)
        main = files["terraform/main.tf"]
        self.assertEqual(main.count("prevent_destroy = true"), 7)
        self.assertIn('version = ">= 4.0, < 5.0"', main)

    def test_bicep_is_split_by_resource_group(self):
        files, _ = compile_estate(INVENTORY, "resource-graph", STATE)
        path = "bicep/rg_commerce_prod.bicep"
        self.assertIn(path, files)
        self.assertIn("targetScope = 'resourceGroup'", files[path])
        self.assertIn("Microsoft.Network/virtualNetworks@2024-05-01", files[path])

    def test_cycle_fails_closed(self):
        cyclic = {
            "resources": [
                {"id": "a", "name": "a", "type": "x/a", "location": "global", "depends_on": ["b"]},
                {"id": "b", "name": "b", "type": "x/b", "location": "global", "depends_on": ["a"]}
            ]
        }
        with self.assertRaisesRegex(ValueError, "dependency cycle"):
            dependency_order(normalize(cyclic, "canonical"))

    def test_outputs_and_receipt_are_written(self):
        files, report = compile_estate(INVENTORY, "resource-graph", STATE)
        self.assertEqual(len(report["receipt"]["content_digest"]), 64)
        with tempfile.TemporaryDirectory() as directory:
            written = write_files(files, directory)
            self.assertTrue(all(path.exists() for path in written))
            stored = json.loads((Path(directory) / "adoption-report.json").read_text())
            self.assertEqual(stored["summary"]["resources"], 8)


if __name__ == "__main__":
    unittest.main()
