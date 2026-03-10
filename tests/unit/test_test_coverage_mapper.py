"""Unit tests for Test Coverage Mapper (Phase 3).

Tests cover:
- Test modules are correctly identified
- Direct imports from test to source module create coverage entry
- Transitive imports propagate coverage
- tests_for_modules returns deduplicated sorted list
- coverage_report has required keys
- to_index_dict is deterministic
- No full-suite fallback: unmapped modules return empty list
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
from tools.test_coverage_mapper import TestCoverageMapper

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_result_with_test_imports() -> ScanResult:
    """
    tests/unit/test_a.py -> agentic_core/adg/schema.py (direct)
    agentic_core/adg/schema.py -> agentic_core/adg/__init__.py (transitive)
    """
    result = ScanResult(commit_sha="t")
    result.modules = [
        "tests/unit/test_a.py",
        "agentic_core/adg/schema.py",
        "agentic_core/adg/__init__.py",
        "agentic_core/adg/cli.py",
    ]
    result.edges = [
        Edge(
            from_name="ADG::Module::tests/unit/test_a.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/adg/schema.py",
            edge_kind="import",
            source_file="tests/unit/test_a.py",
            line_no=2,
        ),
        Edge(
            from_name="ADG::Module::agentic_core/adg/schema.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/adg/__init__.py",
            edge_kind="import",
            source_file="agentic_core/adg/schema.py",
            line_no=3,
        ),
    ]
    result.compute_digest()
    return result


class TestTestModuleIdentification:
    """Test modules under tests/ are correctly classified."""

    @pytest.mark.unit
    def test_test_module_detected(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        assert "tests/unit/test_a.py" in mapper._test_modules

    @pytest.mark.unit
    def test_source_module_not_a_test(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        assert "agentic_core/adg/schema.py" not in mapper._test_modules


class TestDirectImportCoverage:
    """Direct imports from test to source create coverage entries."""

    @pytest.mark.unit
    def test_direct_import_creates_coverage(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_module("agentic_core/adg/schema.py")
        assert "tests/unit/test_a.py" in tests

    @pytest.mark.unit
    def test_uncovered_module_returns_empty(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_module("agentic_core/adg/cli.py")
        assert tests == []

    @pytest.mark.unit
    def test_no_full_suite_fallback(self) -> None:
        """Uncovered module must NOT fall back to all tests."""
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_module("agentic_core/adg/cli.py")
        assert "tests/unit/test_a.py" not in tests


class TestTransitiveCoverage:
    """Tests propagate transitively through import chain."""

    @pytest.mark.unit
    def test_transitive_import_propagates(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        # test_a imports schema, schema imports __init__; so __init__ is transitively covered
        tests = mapper.tests_for_module("agentic_core/adg/__init__.py")
        assert "tests/unit/test_a.py" in tests


class TestTestsForModules:
    """tests_for_modules returns deduplicated sorted list."""

    @pytest.mark.unit
    def test_tests_for_modules_deduplicates(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_modules(
            [
                "agentic_core/adg/schema.py",
                "agentic_core/adg/__init__.py",
            ]
        )
        assert tests.count("tests/unit/test_a.py") == 1

    @pytest.mark.unit
    def test_tests_for_modules_sorted(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_modules(["agentic_core/adg/schema.py"])
        assert tests == sorted(tests)

    @pytest.mark.unit
    def test_tests_for_empty_list_returns_empty(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_modules([])
        assert tests == []


class TestCoverageReport:
    """coverage_report has required keys."""

    @pytest.mark.unit
    def test_coverage_report_has_required_keys(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        report = mapper.coverage_report()
        required = {
            "source_module_count",
            "test_module_count",
            "covered_count",
            "uncovered_count",
            "coverage_pct",
            "uncovered_modules",
            "hotspot_modules",
        }
        assert required <= set(report.keys())

    @pytest.mark.unit
    def test_coverage_pct_between_0_and_100(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        report = mapper.coverage_report()
        assert 0.0 <= report["coverage_pct"] <= 100.0

    @pytest.mark.unit
    def test_covered_plus_uncovered_equals_source(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        report = mapper.coverage_report()
        assert report["covered_count"] + report["uncovered_count"] == report["source_module_count"]


class TestToIndexDict:
    """to_index_dict is deterministic."""

    @pytest.mark.unit
    def test_to_index_dict_has_both_keys(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        idx = mapper.to_index_dict()
        assert "module_to_tests" in idx
        assert "symbol_to_tests" in idx

    @pytest.mark.unit
    def test_to_index_dict_deterministic(self) -> None:
        import json

        result = _make_result_with_test_imports()
        m1 = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        m2 = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        assert json.dumps(m1.to_index_dict(), sort_keys=True) == json.dumps(
            m2.to_index_dict(), sort_keys=True
        )

    @pytest.mark.unit
    def test_build_is_idempotent(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT)
        mapper.build()
        mapper.build()
        tests = mapper.tests_for_module("agentic_core/adg/schema.py")
        assert tests.count("tests/unit/test_a.py") == 1


class TestSortedOutputGuarantees:
    """tests_for_module always returns sorted output."""

    @pytest.mark.unit
    def test_tests_for_module_result_is_sorted(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        tests = mapper.tests_for_module("agentic_core/adg/schema.py")
        assert tests == sorted(tests)

    @pytest.mark.unit
    def test_module_to_tests_values_are_sorted_lists(self) -> None:
        result = _make_result_with_test_imports()
        mapper = TestCoverageMapper(result, repo_root=_REPO_ROOT).build()
        idx = mapper.to_index_dict()
        for module, tests in idx["module_to_tests"].items():
            assert tests == sorted(tests), f"Tests for {module} are not sorted"
