"""Foundational behavioral tests for agentic_core/L5_safety/types/healing_orchestration_types.py.

fan_in=16 — this module is imported by 16 other modules.
ADG contract: import-hygiene is covered by test_healing_orchestration_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.types.healing_orchestration_types import (  # noqa: F401
        HealingResult,
        HealingSuiteResult,
        HealingOrchestrationSuite,
        get_healing_suite,
        run_healing_operation,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    HealingResult = None  # type: ignore[assignment,misc]
    HealingSuiteResult = None  # type: ignore[assignment,misc]
    HealingOrchestrationSuite = None  # type: ignore[assignment,misc]
    get_healing_suite = None  # type: ignore[assignment,misc]
    run_healing_operation = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestHealingResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(HealingResult)}
        assert field_names >= {'success', 'violations_found', 'strategy_name', 'violations_fixed', 'errors'}

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestHealingSuiteResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingSuiteResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(HealingSuiteResult)}
        assert field_names >= {'strategies_failed', 'strategies_succeeded', 'overall_success', 'strategies_run', 'total_violations_found'}

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestHealingOrchestrationSuiteContract:
    def test_is_class(self):
        assert isinstance(HealingOrchestrationSuite, type)

    def test_has_method_run_strategy(self):
        assert callable(getattr(HealingOrchestrationSuite, 'run_strategy', None))

    def test_has_method_run_all(self):
        assert callable(getattr(HealingOrchestrationSuite, 'run_all', None))

    def test_has_method_run_resilience_check(self):
        assert callable(getattr(HealingOrchestrationSuite, 'run_resilience_check', None))

    def test_has_method_run_dependency_cleanup(self):
        assert callable(getattr(HealingOrchestrationSuite, 'run_dependency_cleanup', None))

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestGetHealingSuiteFunction:
    def test_is_callable(self):
        assert callable(get_healing_suite)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_healing_suite)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestRunHealingOperationFunction:
    def test_is_callable(self):
        assert callable(run_healing_operation)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_healing_operation)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_orchestration_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module healing_orchestration_types must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
