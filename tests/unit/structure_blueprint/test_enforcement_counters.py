"""
Regression tests for enforcement module execution counters.

These tests exist to prevent the "green but broken" scenario where enforcement
modules silently iterate over empty iterables and report PASS with zero counters.

The MappingProxyType bug (isinstance(config, dict) → False on mappingproxy)
caused all counters to be zero in v1.  These tests make that unregressable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L5_safety.config.structure_blueprint._constants import (
    SOVEREIGN_TERRITORIES,
)
from agentic_core.L5_safety.config.structure_blueprint.enforcement import (
    blueprint_hash,
    cross_layer,
    leaf_node,
    mixin_ast,
    territory_diff,
    volatile_rules,
)
from agentic_core.L5_safety.config.structure_blueprint.enforcement.import_graph import (
    ImportGraph,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
ENFORCEMENT_REPORT_PATH = REPO_ROOT / "docs" / "reports" / "verification" / "enforcement_report.json"
BLUEPRINT_DIR = REPO_ROOT / "agentic_core" / "L5_safety" / "config" / "structure_blueprint"


class TestTerritoryDiffCounters:
    """territory_diff must check a non-trivial number of territories."""

    def test_territories_checked_nonzero(self) -> None:
        result = territory_diff.check(REPO_ROOT, SOVEREIGN_TERRITORIES)
        checked = result["stats"]["territories_checked"]
        assert checked > 0, (
            f"territory_diff.territories_checked == {checked}; "
            "enforcement is iterating over nothing (MappingProxyType bug?)"
        )

    def test_territories_checked_covers_all_governed(self) -> None:
        result = territory_diff.check(REPO_ROOT, SOVEREIGN_TERRITORIES)
        checked = result["stats"]["territories_checked"]
        assert checked >= 10, (
            f"territory_diff.territories_checked == {checked}; "
            "expected at least 10 territories with subfolder declarations"
        )

    def test_zero_undeclared_subfolders(self) -> None:
        result = territory_diff.check(REPO_ROOT, SOVEREIGN_TERRITORIES)
        undeclared = result["stats"]["undeclared_count"]
        assert undeclared == 0, (
            f"territory_diff found {undeclared} undeclared subfolder(s); "
            "legitimize them in _constants.py or remove from disk"
        )


class TestLeafNodeCounters:
    """leaf_node must check directories with allow_root_py=False."""

    def test_territories_checked_nonzero(self) -> None:
        result = leaf_node.check(REPO_ROOT, SOVEREIGN_TERRITORIES)
        checked = result["stats"]["territories_checked"]
        assert checked > 0, (
            f"leaf_node.territories_checked == {checked}; no territories with allow_root_py=False found"
        )


class TestMixinAstCounters:
    """mixin_ast must check a non-trivial number of files."""

    def test_files_checked_nonzero(self) -> None:
        from collections.abc import Mapping

        ac_config = SOVEREIGN_TERRITORIES.get("agentic_core", {})
        ac_subfolders = ac_config.get("subfolders", {}) if isinstance(ac_config, Mapping) else {}
        result = mixin_ast.check(REPO_ROOT / "agentic_core", ac_subfolders)
        checked = result["stats"]["files_checked"]
        assert checked > 0, f"mixin_ast.files_checked == {checked}; enforcement is iterating over nothing"


class TestVolatileRulesCounters:
    """volatile_rules must detect volatile territories."""

    def test_volatile_territories_nonzero(self) -> None:
        ig = ImportGraph(REPO_ROOT, SOVEREIGN_TERRITORIES)
        result = volatile_rules.check(REPO_ROOT, SOVEREIGN_TERRITORIES, ig)
        vol = result["stats"]["volatile_territories"]
        assert vol > 0, (
            f"volatile_rules.volatile_territories == {vol}; "
            "no volatile territories found in SOVEREIGN_TERRITORIES"
        )


class TestBlueprintHashCounters:
    """blueprint_hash must hash a non-trivial number of files."""

    def test_files_hashed_nonzero(self) -> None:
        result = blueprint_hash.check(BLUEPRINT_DIR)
        hashed = result["stats"]["files_hashed"]
        assert hashed > 0, (
            f"blueprint_hash.files_hashed == {hashed}; no .py files found in blueprint directory"
        )


class TestCrossLayerCounters:
    """cross_layer must analyze a non-trivial number of edges."""

    def test_total_edges_nonzero(self) -> None:
        ig = ImportGraph(REPO_ROOT, SOVEREIGN_TERRITORIES)
        result = cross_layer.check(REPO_ROOT, SOVEREIGN_TERRITORIES, ig)
        edges = result["stats"]["total_edges"]
        assert edges > 0, f"cross_layer.total_edges == {edges}; import graph is empty"

    def test_cross_layer_edges_analyzed_nonzero(self) -> None:
        ig = ImportGraph(REPO_ROOT, SOVEREIGN_TERRITORIES)
        result = cross_layer.check(REPO_ROOT, SOVEREIGN_TERRITORIES, ig)
        analyzed = result["stats"]["cross_layer_edges_analyzed"]
        assert analyzed > 0, (
            f"cross_layer.cross_layer_edges_analyzed == {analyzed}; no cross-layer edges found to analyze"
        )


class TestEnforcementReportArtifact:
    """The enforcement_report.json artifact must be consistent."""

    def test_report_exists(self) -> None:
        assert ENFORCEMENT_REPORT_PATH.is_file(), (
            f"enforcement_report.json not found at {ENFORCEMENT_REPORT_PATH}"
        )

    def test_total_checks_matches_module_count(self) -> None:
        if not ENFORCEMENT_REPORT_PATH.is_file():
            pytest.skip("enforcement_report.json not found")
        report = json.loads(ENFORCEMENT_REPORT_PATH.read_text(encoding="utf-8"))
        expected_modules = 6
        actual = report["summary"]["total_checks"]
        assert actual == expected_modules, (
            f"enforcement_report.json has {actual} checks, expected {expected_modules}"
        )

    def test_no_zero_counter_modules(self) -> None:
        """No enforcement module may report all-zero stats (silent non-execution)."""
        if not ENFORCEMENT_REPORT_PATH.is_file():
            pytest.skip("enforcement_report.json not found")
        report = json.loads(ENFORCEMENT_REPORT_PATH.read_text(encoding="utf-8"))
        for check in report["checks"]:
            name = check["name"]
            stats = check["stats"]
            has_nonzero = any(isinstance(v, (int, float)) and v > 0 for v in stats.values())
            assert has_nonzero, (
                f"Enforcement module '{name}' has all-zero stats: {stats}. "
                "This indicates silent non-execution."
            )


class TestExpiredDebtEnforcement:
    """Expiry enforcement must fail when a debt item has expired."""

    def test_expired_debt_fails(self, monkeypatch, tmp_path: Path) -> None:
        expired_baseline = {
            "ceiling": 3,
            "entries": [
                {
                    "source": "agentic_core/config/core/gateway_config.py",
                    "target": "agentic_core.L2_execution.enforcement.SovereignLLMGateway",
                    "rationale": "test expired debt",
                    "owner": "test",
                    "added": "2000-01-01",
                    "expires": "2000-Q1",
                    "burn_down_plan": "test burn-down",
                },
            ],
        }
        expired_entries = expired_baseline["entries"]
        expired_debt_set = frozenset((e["source"], e["target"]) for e in expired_entries)

        monkeypatch.setattr(cross_layer, "_DEBT_ENTRIES", expired_entries)
        monkeypatch.setattr(cross_layer, "KNOWN_CROSS_LAYER_DEBT", expired_debt_set)
        monkeypatch.setattr(cross_layer, "_DEBT_CEILING", 3)

        ig = ImportGraph(REPO_ROOT, SOVEREIGN_TERRITORIES)
        result = cross_layer.check(REPO_ROOT, SOVEREIGN_TERRITORIES, ig)

        assert result["stats"]["expired_debt_items"] == 1, (
            f"Expected 1 expired debt item, got {result['stats']['expired_debt_items']}"
        )
        assert result["passed"] is False, "cross_layer.check() should FAIL when a debt item has expired"


class TestMappingProxyRegression:
    """Direct regression test for the MappingProxyType bug."""

    def test_sovereign_territories_is_mapping_proxy(self) -> None:
        from types import MappingProxyType

        assert isinstance(SOVEREIGN_TERRITORIES, MappingProxyType), (
            f"SOVEREIGN_TERRITORIES is {type(SOVEREIGN_TERRITORIES).__name__}, expected MappingProxyType"
        )

    def test_ac_config_is_mapping_proxy(self) -> None:
        from collections.abc import Mapping
        from types import MappingProxyType

        ac_config = SOVEREIGN_TERRITORIES["agentic_core"]
        assert isinstance(ac_config, MappingProxyType), (
            f"agentic_core config is {type(ac_config).__name__}, expected MappingProxyType"
        )
        assert isinstance(ac_config, Mapping), (
            "agentic_core config must be a Mapping (ABC); "
            "isinstance(config, dict) would fail on MappingProxyType"
        )

    def test_ac_subfolders_nonempty(self) -> None:
        from collections.abc import Mapping

        ac_config = SOVEREIGN_TERRITORIES["agentic_core"]
        ac_subfolders = ac_config.get("subfolders", {}) if isinstance(ac_config, Mapping) else {}
        assert len(ac_subfolders) > 0, (
            "agentic_core subfolders is empty; the Mapping guard is failing on MappingProxyType"
        )
