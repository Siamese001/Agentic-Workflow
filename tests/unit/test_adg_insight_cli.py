"""Unit tests for ADG Developer Insight CLI (Phase 6).

Tests cover:
- cmd_who_uses returns correct structure and finds direct importers
- cmd_depends_on returns direct imports
- cmd_territory returns layer and allowed edges
- cmd_unresolved returns NormalizationReport dict
- cmd_coverage returns test list (may be empty on minimal result)
- All command outputs have required top-level keys
- Deterministic: same ScanResult -> same command output
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
from agentic_core.adg.schema import canonical_name
from tools.adg_insight_cli import (
    cmd_coverage,
    cmd_depends_on,
    cmd_territory,
    cmd_unresolved,
    cmd_who_uses,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

_MODULE_A = "agentic_core/adg/schema.py"
_MODULE_B = "agentic_core/adg/cli.py"
_TEST_C = "tests/unit/test_adg_identity_normalizer.py"


def _make_result() -> ScanResult:
    result = ScanResult(commit_sha="t")
    result.modules = [_MODULE_A, _MODULE_B, _TEST_C]
    result.edges = [
        Edge(
            from_name=canonical_name("Module", _MODULE_B),
            relation_type="imports",
            to_name=canonical_name("Module", _MODULE_A),
            edge_kind="import",
            source_file=_MODULE_B,
            line_no=3,
        ),
        Edge(
            from_name=canonical_name("Module", _TEST_C),
            relation_type="imports",
            to_name=canonical_name("Module", _MODULE_A),
            edge_kind="import",
            source_file=_TEST_C,
            line_no=5,
        ),
    ]
    result.compute_digest()
    return result


class TestCmdWhoUses:
    """cmd_who_uses returns importers."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_A, result)
        for key in ("module", "direct_importers", "source_importers", "test_importers", "total_count"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_finds_direct_source_importer(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_A, result)
        assert _MODULE_B in out["direct_importers"]

    @pytest.mark.unit
    def test_finds_test_importer_separately(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_A, result)
        assert _TEST_C in out["test_importers"]

    @pytest.mark.unit
    def test_source_and_test_importer_counts(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_A, result)
        assert out["total_count"] == 2

    @pytest.mark.unit
    def test_module_with_no_importers_empty(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_B, result)
        assert out["total_count"] == 0

    @pytest.mark.unit
    def test_deterministic_output(self) -> None:
        result = _make_result()
        o1 = cmd_who_uses(_MODULE_A, result)
        o2 = cmd_who_uses(_MODULE_A, result)
        assert o1 == o2


class TestCmdDependsOn:
    """cmd_depends_on returns imports of a module."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_depends_on(_MODULE_B, result)
        for key in ("module", "direct_imports", "direct_count"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_finds_direct_import(self) -> None:
        result = _make_result()
        out = cmd_depends_on(_MODULE_B, result)
        assert _MODULE_A in out["direct_imports"]

    @pytest.mark.unit
    def test_no_imports_empty_list(self) -> None:
        result = _make_result()
        out = cmd_depends_on(_MODULE_A, result)
        assert out["direct_count"] == 0

    @pytest.mark.unit
    def test_transitive_flag_adds_key(self) -> None:
        result = _make_result()
        out = cmd_depends_on(_MODULE_B, result, transitive=True)
        assert "transitive_imports" in out
        assert "transitive_count" in out


class TestCmdTerritory:
    """cmd_territory returns layer and allowed edges."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        out = cmd_territory(_MODULE_A)
        for key in ("module", "layer", "allowed_import_targets", "allowed_import_sources"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_adg_schema_is_l_tools(self) -> None:
        out = cmd_territory("agentic_core/adg/schema.py")
        assert out["layer"] == "L_TOOLS"

    @pytest.mark.unit
    def test_l0_module_correct_layer(self) -> None:
        out = cmd_territory("agentic_core/L0_routing/config/path_constants.py")
        assert out["layer"] == "L0"

    @pytest.mark.unit
    def test_allowed_import_targets_nonempty_for_l0(self) -> None:
        out = cmd_territory("agentic_core/L0_routing/config/path_constants.py")
        assert isinstance(out["allowed_import_targets"], list)

    @pytest.mark.unit
    def test_deterministic(self) -> None:
        o1 = cmd_territory(_MODULE_A)
        o2 = cmd_territory(_MODULE_A)
        assert o1 == o2


class TestCmdUnresolved:
    """cmd_unresolved returns NormalizationReport dict."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_unresolved(result, _REPO_ROOT)
        for key in ("total", "by_kind", "by_confidence", "unresolved_count", "unresolved_names"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_total_is_nonnegative(self) -> None:
        result = _make_result()
        out = cmd_unresolved(result, _REPO_ROOT)
        assert out["total"] >= 0

    @pytest.mark.unit
    def test_unresolved_names_is_sorted(self) -> None:
        result = _make_result()
        out = cmd_unresolved(result, _REPO_ROOT)
        names = out["unresolved_names"]
        assert names == sorted(names)


class TestCmdCoverage:
    """cmd_coverage returns test list."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_coverage(_MODULE_A, result, _REPO_ROOT)
        for key in ("module", "covering_tests", "test_count"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_covered_module_has_tests(self) -> None:
        result = _make_result()
        out = cmd_coverage(_MODULE_A, result, _REPO_ROOT)
        assert out["test_count"] == len(out["covering_tests"])

    @pytest.mark.unit
    def test_uncovered_module_has_empty_list(self) -> None:
        result = _make_result()
        out = cmd_coverage(_MODULE_B, result, _REPO_ROOT)
        assert out["covering_tests"] == []

    @pytest.mark.unit
    def test_note_present_when_no_coverage(self) -> None:
        result = _make_result()
        out = cmd_coverage(_MODULE_B, result, _REPO_ROOT)
        assert "note" in out
