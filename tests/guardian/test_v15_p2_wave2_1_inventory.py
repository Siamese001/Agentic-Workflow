"""
Guardian test: Wave 2.1 Runtime Entry-Point Inventory.

Validates that the Phase 2 Wave 2.1 inventory artifact exists, conforms to
the required schema, and contains non-trivial content.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

INVENTORY_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reports"
    / "plans"
    / "v15_phase2_wave2_1_runtime_entrypoints.json"
)

REQUIRED_CATEGORIES = {"A", "B", "C", "D", "E"}
VALID_BYPASS_RISKS = {"NONE", "LOW", "MEDIUM", "HIGH"}
VALID_SIDE_EFFECT_TYPES = {
    "file_write",
    "state_mutation",
    "tool_call",
    "artifact_emit",
    "schedule",
    "retry",
    "network_call",
}


@pytest.fixture(scope="module")
def inventory() -> dict:
    """Load and return the inventory JSON."""
    assert INVENTORY_PATH.exists(), f"Inventory file missing: {INVENTORY_PATH}"
    text = INVENTORY_PATH.read_text(encoding="utf-8")
    data = json.loads(text)
    return data


class TestWave21InventoryPresence:
    """Verify the inventory file exists and is loadable."""

    def test_inventory_file_exists(self) -> None:
        assert INVENTORY_PATH.exists(), f"Inventory file missing: {INVENTORY_PATH}"

    def test_inventory_is_valid_json(self) -> None:
        text = INVENTORY_PATH.read_text(encoding="utf-8")
        data = json.loads(text)
        assert isinstance(data, dict)


class TestWave21SchemaCompliance:
    """Validate schema_version and top-level keys."""

    def test_schema_version(self, inventory: dict) -> None:
        assert inventory.get("schema_version") == "2.1.0"

    def test_required_top_level_keys(self, inventory: dict) -> None:
        required = {"schema_version", "generated_utc", "repo_root", "scope_rule", "entrypoints", "counts"}
        missing = required - set(inventory.keys())
        assert not missing, f"Missing top-level keys: {missing}"

    def test_scope_rule_non_empty(self, inventory: dict) -> None:
        assert len(inventory.get("scope_rule", "")) > 20, "scope_rule must be a substantive definition"


class TestWave21EntrypointIntegrity:
    """Validate entrypoint entries are well-formed and non-empty."""

    def test_entrypoints_non_empty(self, inventory: dict) -> None:
        eps = inventory.get("entrypoints", [])
        assert len(eps) > 0, "entrypoints must contain at least one entry"

    def test_no_duplicate_ids(self, inventory: dict) -> None:
        ids = [ep["id"] for ep in inventory["entrypoints"]]
        duplicates = [eid for eid in ids if ids.count(eid) > 1]
        assert not duplicates, f"Duplicate entrypoint ids: {set(duplicates)}"

    def test_every_entry_has_enforcement_boundary(self, inventory: dict) -> None:
        missing = [ep["id"] for ep in inventory["entrypoints"] if not ep.get("enforcement_boundary")]
        assert not missing, f"Entries missing enforcement_boundary: {missing}"

    def test_every_entry_has_valid_category(self, inventory: dict) -> None:
        invalid = [
            ep["id"] for ep in inventory["entrypoints"] if ep.get("category") not in REQUIRED_CATEGORIES
        ]
        assert not invalid, f"Entries with invalid category: {invalid}"

    def test_every_entry_has_valid_bypass_risk(self, inventory: dict) -> None:
        invalid = [
            ep["id"] for ep in inventory["entrypoints"] if ep.get("bypass_risk") not in VALID_BYPASS_RISKS
        ]
        assert not invalid, f"Entries with invalid bypass_risk: {invalid}"

    def test_every_entry_has_valid_side_effect_types(self, inventory: dict) -> None:
        invalid = []
        for ep in inventory["entrypoints"]:
            bad = set(ep.get("side_effect_types", [])) - VALID_SIDE_EFFECT_TYPES
            if bad:
                invalid.append((ep["id"], bad))
        assert not invalid, f"Entries with invalid side_effect_types: {invalid}"

    def test_required_entry_fields(self, inventory: dict) -> None:
        required_fields = {
            "id",
            "category",
            "path",
            "symbol",
            "signature",
            "initiates_side_effects",
            "side_effect_types",
            "calls_heal",
            "already_v15_enforced",
            "enforcement_boundary",
            "bypass_risk",
            "notes",
        }
        for ep in inventory["entrypoints"]:
            missing = required_fields - set(ep.keys())
            assert not missing, f"Entry {ep.get('id', '?')} missing fields: {missing}"


class TestWave21Counts:
    """Validate counts section matches actual entrypoint data."""

    def test_total_matches_entrypoints_length(self, inventory: dict) -> None:
        actual = len(inventory["entrypoints"])
        declared = inventory["counts"]["total"]
        assert actual == declared, f"counts.total={declared} but {actual} entrypoints found"

    def test_by_category_sums_to_total(self, inventory: dict) -> None:
        by_cat = inventory["counts"]["by_category"]
        cat_sum = sum(by_cat.values())
        total = inventory["counts"]["total"]
        assert cat_sum == total, f"by_category sum={cat_sum} != total={total}"

    def test_by_category_matches_actual(self, inventory: dict) -> None:
        from collections import Counter

        actual = Counter(ep["category"] for ep in inventory["entrypoints"])
        declared = inventory["counts"]["by_category"]
        for cat in REQUIRED_CATEGORIES:
            assert actual.get(cat, 0) == declared.get(cat, 0), (
                f"Category {cat}: actual={actual.get(cat, 0)} != declared={declared.get(cat, 0)}"
            )

    def test_already_v15_enforced_count(self, inventory: dict) -> None:
        actual = sum(1 for ep in inventory["entrypoints"] if ep.get("already_v15_enforced"))
        declared = inventory["counts"]["already_v15_enforced"]
        assert actual == declared, f"already_v15_enforced: actual={actual} != declared={declared}"

    def test_bypass_risk_high_count(self, inventory: dict) -> None:
        actual = sum(1 for ep in inventory["entrypoints"] if ep.get("bypass_risk") == "HIGH")
        declared = inventory["counts"]["bypass_risk_high"]
        assert actual == declared, f"bypass_risk_high: actual={actual} != declared={declared}"


class TestWave21MECECoverage:
    """Validate MECE coverage across categories."""

    def test_all_categories_represented(self, inventory: dict) -> None:
        present = {ep["category"] for ep in inventory["entrypoints"]}
        missing = REQUIRED_CATEGORIES - present
        assert not missing, f"Categories with zero entries: {missing}"

    def test_no_heal_only_entries(self, inventory: dict) -> None:
        heal_only = [
            ep["id"]
            for ep in inventory["entrypoints"]
            if ep.get("calls_heal") and not ep.get("initiates_side_effects")
        ]
        assert not heal_only, f"Entries that only call heal (out of scope): {heal_only}"
