"""Behavioral tests for ``agentic_core.L5_safety.types.healing_orchestration_types``.

Covers:
- HealingResult / HealingSuiteResult dataclass construction + defaults + timestamps.
- HealingOrchestrationSuite.run_strategy: unknown strategy, can_heal=False skip,
  successful heal, value/type error trapped.
- HealingOrchestrationSuite.run_all aggregates results and counts.
- get_healing_suite singleton reuse.
- run_healing_operation convenience delegates to get_healing_suite().run_all.
"""

from __future__ import annotations

from typing import Any

import pytest

import agentic_core.L5_safety.types.healing_orchestration_types as hot_mod
from agentic_core.L5_safety.types.healing_orchestration_types import (
    HealingOrchestrationSuite,
    HealingResult,
    HealingSuiteResult,
    get_healing_suite,
    run_healing_operation,
)


# ---- Fake strategies for injection into the private _strategies map -----

class _Strategy:
    """Minimal duck-typed strategy matching what run_strategy expects."""

    def __init__(
        self,
        *,
        can: bool = True,
        heal_result: dict[str, Any] | None = None,
        raise_exc: type[BaseException] | None = None,
    ) -> None:
        self._can = can
        self._result = heal_result or {"success": True, "violations_found": 1, "violations_fixed": 1}
        self._raise = raise_exc

    def can_heal(self, violation: dict) -> bool:  # noqa: ARG002
        return self._can

    def heal(self, violation: dict, context: dict) -> dict[str, Any]:  # noqa: ARG002
        if self._raise is not None:
            raise self._raise("boom")
        return self._result


def _suite_with(strategies: dict[str, Any]) -> HealingOrchestrationSuite:
    """Build a suite with the given strategies, bypassing lazy init of real ones."""
    suite = HealingOrchestrationSuite()
    suite._strategies = strategies  # type: ignore[attr-defined]
    suite._initialized = True  # type: ignore[attr-defined]
    return suite


# ---- HealingResult / HealingSuiteResult ---------------------------------

class TestHealingResultDefaults:
    def test_minimal(self) -> None:
        r = HealingResult(strategy_name="s", success=True)
        assert r.violations_found == 0
        assert r.violations_fixed == 0
        assert r.errors == []
        assert r.metadata == {}
        assert r.timestamp  # ISO-like string

    def test_with_fields(self) -> None:
        r = HealingResult(
            strategy_name="s", success=False,
            violations_found=3, violations_fixed=1,
            errors=["e1"], metadata={"k": "v"},
        )
        assert r.errors == ["e1"]
        assert r.metadata == {"k": "v"}


class TestHealingSuiteResultDefaults:
    def test_defaults(self) -> None:
        sr = HealingSuiteResult(
            overall_success=True, strategies_run=0, strategies_succeeded=0,
            strategies_failed=0, total_violations_found=0, total_violations_fixed=0,
        )
        assert sr.results == []
        assert sr.execution_time_ms == 0.0
        assert sr.timestamp  # populated


# ---- run_strategy --------------------------------------------------------

class TestRunStrategy:
    def test_unknown_strategy_returns_failure(self) -> None:
        suite = _suite_with({})
        r = suite.run_strategy("missing", violation={"type": "x"})
        assert r.success is False
        assert r.strategy_name == "missing"
        assert any("not found" in e for e in r.errors)

    def test_can_heal_false_is_skipped_as_success(self) -> None:
        suite = _suite_with({"s1": _Strategy(can=False)})
        r = suite.run_strategy("s1", violation={"type": "x"})
        assert r.success is True
        assert r.metadata.get("skipped") is True
        assert r.metadata.get("reason") == "violation_type_not_supported"

    def test_successful_heal(self) -> None:
        strategy = _Strategy(heal_result={
            "success": True, "violations_found": 2,
            "violations_fixed": 2, "errors": [], "extra": "meta",
        })
        suite = _suite_with({"s1": strategy})
        r = suite.run_strategy("s1", violation={"type": "x"})
        assert r.success is True
        assert r.violations_found == 2
        assert r.violations_fixed == 2
        assert r.metadata == {"extra": "meta"}

    def test_failed_heal_zeroes_fixed(self) -> None:
        strategy = _Strategy(heal_result={
            "success": False, "violations_found": 2,
            "violations_fixed": 2, "errors": ["oh no"],
        })
        suite = _suite_with({"s1": strategy})
        r = suite.run_strategy("s1", violation={"type": "x"})
        assert r.success is False
        assert r.violations_fixed == 0  # zeroed per contract
        assert r.errors == ["oh no"]

    @pytest.mark.parametrize("exc", [ValueError, TypeError])
    def test_heal_exception_trapped(self, exc: type[BaseException]) -> None:
        suite = _suite_with({"s1": _Strategy(raise_exc=exc)})
        r = suite.run_strategy("s1", violation={"type": "x"})
        assert r.success is False
        assert any("Strategy error" in e for e in r.errors)

    def test_context_defaults_to_empty_dict(self) -> None:
        captured: list[dict] = []

        class Capture:
            def can_heal(self, v: dict) -> bool:  # noqa: ARG002
                return True

            def heal(self, v: dict, ctx: dict) -> dict:  # noqa: ARG002
                captured.append(ctx)
                return {"success": True}

        suite = _suite_with({"s1": Capture()})
        suite.run_strategy("s1", violation={"type": "x"}, context=None)
        assert captured == [{}]


# ---- run_all -------------------------------------------------------------

class TestRunAll:
    def test_aggregates_success(self) -> None:
        suite = _suite_with({
            "a": _Strategy(heal_result={
                "success": True, "violations_found": 3, "violations_fixed": 3,
            }),
            "b": _Strategy(heal_result={
                "success": True, "violations_found": 2, "violations_fixed": 2,
            }),
        })
        sr = suite.run_all(violation={"type": "x"})
        assert sr.strategies_run == 2
        assert sr.strategies_succeeded == 2
        assert sr.strategies_failed == 0
        assert sr.overall_success is True
        assert sr.total_violations_found == 5
        assert sr.total_violations_fixed == 5
        assert sr.execution_time_ms >= 0.0

    def test_partial_failure_marks_overall_failure(self) -> None:
        suite = _suite_with({
            "a": _Strategy(heal_result={"success": True, "violations_found": 1, "violations_fixed": 1}),
            "b": _Strategy(heal_result={"success": False, "violations_found": 1}),
        })
        sr = suite.run_all(violation={"type": "x"})
        assert sr.overall_success is False
        assert sr.strategies_failed == 1
        assert sr.strategies_succeeded == 1

    def test_no_strategies(self) -> None:
        suite = _suite_with({})
        sr = suite.run_all(violation={"type": "x"})
        assert sr.strategies_run == 0
        assert sr.overall_success is True  # 0 failed


# ---- Singleton / convenience --------------------------------------------

class TestSingleton:
    def setup_method(self) -> None:
        # Reset the module-level singleton each test
        hot_mod._healing_suite = None

    def teardown_method(self) -> None:
        hot_mod._healing_suite = None

    def test_singleton_returns_same_instance(self) -> None:
        s1 = get_healing_suite()
        s2 = get_healing_suite()
        assert s1 is s2

    def test_run_healing_operation_delegates(self) -> None:
        suite = _suite_with({
            "a": _Strategy(heal_result={"success": True, "violations_found": 1, "violations_fixed": 1}),
        })
        hot_mod._healing_suite = suite
        result = run_healing_operation(violation={"type": "x"})
        assert isinstance(result, HealingSuiteResult)
        assert result.strategies_run == 1
        assert result.overall_success is True


# ---- Convenience wrappers -----------------------------------------------

class TestConvenienceWrappers:
    def test_run_resilience_check_uses_chaos_strategy(self) -> None:
        strategy = _Strategy(heal_result={"success": True, "violations_found": 1, "violations_fixed": 1})
        suite = _suite_with({"chaos_resilience": strategy})
        r = suite.run_resilience_check()
        assert r.strategy_name == "chaos_resilience"
        assert r.success is True

    def test_run_dependency_cleanup_passes_dry_run(self) -> None:
        captured: list[dict] = []

        class Capture:
            def can_heal(self, v: dict) -> bool:  # noqa: ARG002
                return True

            def heal(self, v: dict, ctx: dict) -> dict:  # noqa: ARG002
                captured.append(ctx)
                return {"success": True}

        suite = _suite_with({"dependency_pruning": Capture()})
        suite.run_dependency_cleanup(dry_run=False, context={"extra": 1})
        assert captured == [{"extra": 1, "dry_run": False}]

    def test_get_available_strategies(self) -> None:
        suite = _suite_with({"a": _Strategy(), "b": _Strategy()})
        assert set(suite.get_available_strategies()) == {"a", "b"}

    def test_get_status(self) -> None:
        suite = _suite_with({"a": _Strategy()})
        s = suite.get_status()
        assert s["initialized"] is True
        assert s["strategy_count"] == 1
        assert s["strategies_available"] == ["a"]
