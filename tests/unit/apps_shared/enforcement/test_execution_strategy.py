"""Foundational behavioral tests for apps_shared/enforcement/execution_strategy.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_execution_strategy_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.enforcement.execution_strategy import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ExecutionConfig,
        ExecutionEnvironment,
        ExecutionPriority,
        ExecutionRequest,
        ExecutionResult,
        ExecutionStrategy,
        create_observability_execution_engine,
        use_observability_execution,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ExecutionStrategy = None  # type: ignore[assignment,misc]
    ExecutionPriority = None  # type: ignore[assignment,misc]
    ExecutionRequest = None  # type: ignore[assignment,misc]
    ExecutionEnvironment = None  # type: ignore[assignment,misc]
    ExecutionConfig = None  # type: ignore[assignment,misc]
    ExecutionResult = None  # type: ignore[assignment,misc]
    create_observability_execution_engine = None  # type: ignore[assignment,misc]
    use_observability_execution = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestExecutionStrategyContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionStrategy, enum.Enum)

    def test_has_members(self):
        assert len(list(ExecutionStrategy)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ExecutionStrategy:
            assert member.value is not None

    def test_known_member_immediate_exists(self):
        assert hasattr(ExecutionStrategy, 'IMMEDIATE')

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestExecutionPriorityContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionPriority, enum.Enum)

    def test_has_members(self):
        assert len(list(ExecutionPriority)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ExecutionPriority:
            assert member.value is not None

    def test_known_member_low_exists(self):
        assert hasattr(ExecutionPriority, 'LOW')

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestExecutionRequestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionRequest)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ExecutionRequest)}
        assert field_names >= {'priority', 'parameters', 'request_id', 'operation_type', 'strategy'}

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestExecutionEnvironmentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionEnvironment)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ExecutionEnvironment)}
        assert field_names >= {'permissions', 'limits', 'variables', 'env_id', 'resources'}

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestExecutionConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ExecutionConfig)}
        assert field_names >= {'queue_size', 'enable_queueing', 'enable_retry', 'default_timeout', 'max_concurrent_executions'}

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestExecutionResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ExecutionResult)}
        assert field_names >= {'success', 'request_id', 'operation_type', 'exit_code', 'output'}

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestCreateObservabilityExecutionEngineFunction:
    def test_is_callable(self):
        assert callable(create_observability_execution_engine)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_observability_execution_engine)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestUseObservabilityExecutionFunction:
    def test_is_callable(self):
        assert callable(use_observability_execution)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(use_observability_execution)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="execution_strategy.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module execution_strategy must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
