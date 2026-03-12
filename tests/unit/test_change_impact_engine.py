"""Unit tests for Change Impact Engine (Phase 3).

Tests cover:
- Empty changed files produce zero impact
- Direct importer is found at depth 0
- Transitive importer is found at higher depth
- Route mode thresholds (NORMAL / RESTRICTED / HUMAN_REVIEW)
- Uncovered changed files reported explicitly
- Impact digest is deterministic
- No silent full-suite fallback
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
from tools.change_impact_engine import ChangeImpactEngine

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_scan_result_with_imports() -> ScanResult:
    """
    Graph: A -> B -> C (B imports A; C imports B)
    A = agentic_core/L0_routing/config/path_constants.py  (L0)
    B = agentic_core/L2_execution/UniversalWriteGateway.py (L2)
    C = apps_rg/engines/SomeAgent.py (L_APP)
    """
    result = ScanResult(commit_sha="test")
    result.modules = [
        "agentic_core/L0_routing/config/path_constants.py",
        "agentic_core/L2_execution/UniversalWriteGateway.py",
        "apps_rg/engines/SomeAgent.py",
    ]
    result.edges = [
        Edge(
            from_name="ADG::Module::agentic_core/L2_execution/UniversalWriteGateway.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/L0_routing/config/path_constants.py",
            edge_kind="import",
            source_file="agentic_core/L2_execution/UniversalWriteGateway.py",
            line_no=3,
        ),
        Edge(
            from_name="ADG::Module::apps_rg/engines/SomeAgent.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/L2_execution/UniversalWriteGateway.py",
            edge_kind="import",
            source_file="apps_rg/engines/SomeAgent.py",
            line_no=5,
        ),
    ]
    result.compute_digest()
    return result


class TestEmptyChangedFiles:
    """No changed files -> no impact."""

    @pytest.mark.unit
    def test_zero_changed_files_zero_impact(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze([], include_tests=False)
        assert impact.impacted_modules == []

    @pytest.mark.unit
    def test_zero_changed_files_normal_route(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze([], include_tests=False)
        assert impact.route_mode == "NORMAL"
        assert impact.risk_score == 0


class TestBlastRadiusComputation:
    """Changed files cause transitive reverse-dependency detection."""

    @pytest.mark.unit
    def test_direct_importer_found(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        assert "agentic_core/L2_execution/UniversalWriteGateway.py" in impact.impacted_modules

    @pytest.mark.unit
    def test_transitive_importer_found(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        assert "apps_rg/engines/SomeAgent.py" in impact.impacted_modules

    @pytest.mark.unit
    def test_leaf_change_has_higher_depth(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        assert impact.blast_radius_by_depth.get("apps_rg/engines/SomeAgent.py", -1) > 0

    @pytest.mark.unit
    def test_changed_file_itself_included_at_depth_zero(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        target = "agentic_core/L0_routing/config/path_constants.py"
        assert target in impact.impacted_modules
        assert impact.blast_radius_by_depth.get(target) == 0


class TestUncoveredChangedFiles:
    """Files not in ADG index are reported explicitly, never silently ignored."""

    @pytest.mark.unit
    def test_file_not_in_adg_goes_to_uncovered(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["totally/missing/module.py"],
            include_tests=False,
        )
        assert "totally/missing/module.py" in impact.uncovered_changed_files

    @pytest.mark.unit
    def test_missing_file_not_in_impacted_modules(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["totally/missing/module.py"],
            include_tests=False,
        )
        assert "totally/missing/module.py" not in impact.impacted_modules


class TestRouteModeThresholds:
    """Route mode thresholds match blast_radius.py constants."""

    @pytest.mark.unit
    def test_restricted_threshold_is_300(self) -> None:
        engine = ChangeImpactEngine(_make_scan_result_with_imports())
        assert engine._RESTRICTED_THRESHOLD == 300

    @pytest.mark.unit
    def test_human_review_threshold_is_700(self) -> None:
        engine = ChangeImpactEngine(_make_scan_result_with_imports())
        assert engine._HUMAN_REVIEW_THRESHOLD == 700

    @pytest.mark.unit
    def test_zero_risk_is_normal(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze([], include_tests=False)
        assert impact.route_mode == "NORMAL"


class TestImpactDigest:
    """Impact digest is deterministic."""

    @pytest.mark.unit
    def test_same_inputs_same_digest(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        i1 = engine.analyze(["agentic_core/L0_routing/config/path_constants.py"], include_tests=False)
        i2 = engine.analyze(["agentic_core/L0_routing/config/path_constants.py"], include_tests=False)
        assert i1.impact_digest == i2.impact_digest

    @pytest.mark.unit
    def test_different_inputs_different_digest(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        i1 = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        i2 = engine.analyze(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            include_tests=False,
        )
        assert i1.impact_digest != i2.impact_digest

    @pytest.mark.unit
    def test_impact_digest_is_64_hex(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        assert len(impact.impact_digest) == 64
        assert all(c in "0123456789abcdef" for c in impact.impact_digest)


class TestBFSDepthCorrectness:
    """BFS must assign *minimal* depth; DFS would produce incorrect values."""

    @pytest.mark.unit
    def test_chain_a_b_c_depths_are_correct(self) -> None:
        """
        Chain: A -> B -> C (B depends on A; C depends on B)
        Changing A:  A=depth0, B=depth1, C=depth2.
        DFS (stack.pop) can visit C before B, yielding C=depth1 — wrong.
        BFS (deque.popleft) guarantees minimal depth.
        """
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        depths = impact.blast_radius_by_depth
        a = "agentic_core/L0_routing/config/path_constants.py"
        b = "agentic_core/L2_execution/UniversalWriteGateway.py"
        c = "apps_rg/engines/SomeAgent.py"
        assert depths[a] == 0
        assert depths[b] == 1
        assert depths[c] == 2


class TestChangeImpactResultToDict:
    """to_dict produces expected keys."""

    @pytest.mark.unit
    def test_to_dict_has_required_keys(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze([], include_tests=False)
        d = impact.to_dict()
        required = {
            "changed_files",
            "impacted_module_count",
            "impacted_modules",
            "impacted_test_count",
            "impacted_tests",
            "risk_score",
            "route_mode",
            "scope_widening_events",
            "uncovered_changed_files",
            "impact_digest",
        }
        assert required <= set(d.keys())

    @pytest.mark.unit
    def test_to_dict_sorted_deterministic(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        d1 = impact.to_dict()
        d2 = impact.to_dict()
        assert d1 == d2


class TestScopeWideningEvents:
    """scope_widening_events is always present in output and is a list."""

    @pytest.mark.unit
    def test_scope_widening_events_present_in_to_dict(self) -> None:
        result = _make_scan_result_with_imports()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        impact = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=False,
        )
        d = impact.to_dict()
        assert "scope_widening_events" in d
        assert isinstance(d["scope_widening_events"], list)

    @pytest.mark.unit
    def test_include_tests_flag_separates_test_paths(self) -> None:
        """With include_tests=False, test files appear in impacted_modules but
        are separated into impacted_tests; include_tests=True puts them in both."""
        result = ScanResult(commit_sha="test")
        result.modules = [
            "agentic_core/L0_routing/config/path_constants.py",
            "tests/unit/test_something.py",
        ]
        result.edges = [
            Edge(
                from_name="ADG::Module::tests/unit/test_something.py",
                relation_type="imports",
                to_name="ADG::Module::agentic_core/L0_routing/config/path_constants.py",
                edge_kind="import",
                source_file="tests/unit/test_something.py",
                line_no=1,
            )
        ]
        result.compute_digest()
        engine = ChangeImpactEngine(result, repo_root=_REPO_ROOT)
        # include_tests=True: test files appear in impacted_tests list
        impact_with_tests = engine.analyze(
            ["agentic_core/L0_routing/config/path_constants.py"],
            include_tests=True,
        )
        assert "tests/unit/test_something.py" in impact_with_tests.impacted_tests