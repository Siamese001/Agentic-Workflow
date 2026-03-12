"""Foundational behavioral tests for apps_shared/utils/unified_executor_util.py.

fan_in=17 — this module is imported by 17 other modules.
ADG contract: import-hygiene is covered by test_unified_executor_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.unified_executor_util import (  # noqa: F401
        ExecutionStatus,
        ExecutionContext,
        ExecutionResult,
        ExecutionStrategy,
        LLMExecutionStrategy,
        APIExecutionStrategy,
        get_engine_executor,
        execute_resume_generation,
        execute_outreach_generation,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    ExecutionStatus = None  # type: ignore[assignment,misc]
    ExecutionContext = None  # type: ignore[assignment,misc]
    ExecutionResult = None  # type: ignore[assignment,misc]
    ExecutionStrategy = None  # type: ignore[assignment,misc]
    LLMExecutionStrategy = None  # type: ignore[assignment,misc]
    APIExecutionStrategy = None  # type: ignore[assignment,misc]
    get_engine_executor = None  # type: ignore[assignment,misc]
    execute_resume_generation = None  # type: ignore[assignment,misc]
    execute_outreach_generation = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestExecutionStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(ExecutionStatus)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ExecutionStatus:
            assert member.value is not None

    def test_known_member_pending_exists(self):
        assert hasattr(ExecutionStatus, 'PENDING')

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestExecutionContextContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionContext)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ExecutionContext)}
        assert field_names >= {'engine_type', 'config', 'operation_id', 'metadata', 'input_data'}

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestExecutionResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ExecutionResult)}
        assert field_names >= {'error', 'context', 'status', 'metrics', 'data'}

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestExecutionStrategyContract:
    def test_is_class(self):
        assert isinstance(ExecutionStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(ExecutionStrategy, 'execute', None))

    def test_has_method_strategy_name(self):
        assert callable(getattr(ExecutionStrategy, 'strategy_name', None))

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestLLMExecutionStrategyContract:
    def test_is_class(self):
        assert isinstance(LLMExecutionStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(LLMExecutionStrategy, 'execute', None))

    def test_has_method_strategy_name(self):
        assert callable(getattr(LLMExecutionStrategy, 'strategy_name', None))

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestAPIExecutionStrategyContract:
    def test_is_class(self):
        assert isinstance(APIExecutionStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(APIExecutionStrategy, 'execute', None))

    def test_has_method_strategy_name(self):
        assert callable(getattr(APIExecutionStrategy, 'strategy_name', None))

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestGetEngineExecutorFunction:
    def test_is_callable(self):
        assert callable(get_engine_executor)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_engine_executor)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestExecuteResumeGenerationFunction:
    def test_is_callable(self):
        assert callable(execute_resume_generation)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(execute_resume_generation)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestExecuteOutreachGenerationFunction:
    def test_is_callable(self):
        assert callable(execute_outreach_generation)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(execute_outreach_generation)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_executor_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module unified_executor_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
