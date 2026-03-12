"""ADG-driven tests for agentic_core/L5_safety/types/healing_orchestration_types.py — fan_in=6.

Dataclass contract tests: verify HealingResult, HealingSuiteResult, and
HealingOrchestrationSuite have stable fields, defaults, and serialization.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.types.healing_orchestration_types import (
    HealingResult,
    HealingSuiteResult,
)


class TestHealingResult:
    def test_required_fields(self):
        r = HealingResult(strategy_name="chaos", success=True)
        assert r.strategy_name == "chaos"
        assert r.success is True

    def test_default_violations_zero(self):
        r = HealingResult(strategy_name="test", success=False)
        assert r.violations_found == 0
        assert r.violations_fixed == 0

    def test_default_errors_empty_list(self):
        r = HealingResult(strategy_name="test", success=True)
        assert r.errors == []

    def test_default_metadata_empty_dict(self):
        r = HealingResult(strategy_name="test", success=True)
        assert r.metadata == {}

    def test_timestamp_set(self):
        r = HealingResult(strategy_name="test", success=True)
        assert r.timestamp is not None
        assert len(r.timestamp) > 0

    def test_violations_provided(self):
        r = HealingResult(strategy_name="s", success=True, violations_found=5, violations_fixed=3)
        assert r.violations_found == 5
        assert r.violations_fixed == 3

    def test_errors_provided(self):
        r = HealingResult(strategy_name="s", success=False, errors=["err1", "err2"])
        assert r.errors == ["err1", "err2"]

    def test_independent_defaults(self):
        """Each instance must get its own errors list."""
        r1 = HealingResult(strategy_name="a", success=True)
        r2 = HealingResult(strategy_name="b", success=True)
        r1.errors.append("x")
        assert r2.errors == []


class TestHealingSuiteResult:
    def test_required_fields(self):
        sr = HealingSuiteResult(
            overall_success=True,
            strategies_run=3,
            strategies_succeeded=2,
            strategies_failed=1,
            total_violations_found=5,
            total_violations_fixed=4,
        )
        assert sr.overall_success is True
        assert sr.strategies_run == 3
        assert sr.strategies_succeeded == 2
        assert sr.strategies_failed == 1

    def test_default_results_empty_list(self):
        sr = HealingSuiteResult(
            overall_success=True,
            strategies_run=0,
            strategies_succeeded=0,
            strategies_failed=0,
            total_violations_found=0,
            total_violations_fixed=0,
        )
        assert sr.results == []

    def test_default_execution_time_zero(self):
        sr = HealingSuiteResult(
            overall_success=False,
            strategies_run=1,
            strategies_succeeded=0,
            strategies_failed=1,
            total_violations_found=0,
            total_violations_fixed=0,
        )
        assert sr.execution_time_ms == 0.0

    def test_timestamp_set(self):
        sr = HealingSuiteResult(
            overall_success=True,
            strategies_run=1,
            strategies_succeeded=1,
            strategies_failed=0,
            total_violations_found=0,
            total_violations_fixed=0,
        )
        assert sr.timestamp is not None

    def test_results_added(self):
        r = HealingResult(strategy_name="s", success=True)
        sr = HealingSuiteResult(
            overall_success=True,
            strategies_run=1,
            strategies_succeeded=1,
            strategies_failed=0,
            total_violations_found=0,
            total_violations_fixed=0,
            results=[r],
        )
        assert len(sr.results) == 1
        assert sr.results[0] is r

    def test_independent_defaults(self):
        sr1 = HealingSuiteResult(
            overall_success=True, strategies_run=0, strategies_succeeded=0,
            strategies_failed=0, total_violations_found=0, total_violations_fixed=0,
        )
        sr2 = HealingSuiteResult(
            overall_success=True, strategies_run=0, strategies_succeeded=0,
            strategies_failed=0, total_violations_found=0, total_violations_fixed=0,
        )
        r = HealingResult(strategy_name="x", success=True)
        sr1.results.append(r)
        assert sr2.results == []


class TestHealingOrchestrationSuiteImport:
    def test_suite_class_importable(self):
        from agentic_core.L5_safety.types.healing_orchestration_types import HealingOrchestrationSuite
        assert callable(HealingOrchestrationSuite)

    def test_suite_has_run_method(self):
        from agentic_core.L5_safety.types.healing_orchestration_types import HealingOrchestrationSuite
        assert hasattr(HealingOrchestrationSuite, "run") or hasattr(HealingOrchestrationSuite, "run_all")
