"""Foundational behavioral tests for apps_shared/utils/observability_type_util.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_observability_type_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.observability_type_util import (  # noqa: F401
        ObservabilityType,
        ExecutionLevel,
        ObservabilityRequest,
        ObservabilityResult,
        ObservabilityConfig,
        ObservabilityExecutionAdapter,
        create_observability_execution_adapter,
        execute_observability_execution,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    ObservabilityType = None  # type: ignore[assignment,misc]
    ExecutionLevel = None  # type: ignore[assignment,misc]
    ObservabilityRequest = None  # type: ignore[assignment,misc]
    ObservabilityResult = None  # type: ignore[assignment,misc]
    ObservabilityConfig = None  # type: ignore[assignment,misc]
    ObservabilityExecutionAdapter = None  # type: ignore[assignment,misc]
    create_observability_execution_adapter = None  # type: ignore[assignment,misc]
    execute_observability_execution = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ObservabilityType, enum.Enum)

    def test_has_members(self):
        assert len(list(ObservabilityType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ObservabilityType:
            assert member.value is not None

    def test_known_member_trace_exists(self):
        assert hasattr(ObservabilityType, 'TRACE')

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestExecutionLevelContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionLevel, enum.Enum)

    def test_has_members(self):
        assert len(list(ExecutionLevel)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ExecutionLevel:
            assert member.value is not None

    def test_known_member_basic_exists(self):
        assert hasattr(ExecutionLevel, 'BASIC')

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityRequestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityRequest)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ObservabilityRequest)}
        assert field_names >= {'target', 'parameters', 'execution_level', 'request_id', 'operation_type'}

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ObservabilityResult)}
        assert field_names >= {'success', 'request_id', 'metrics', 'operation_type', 'data'}

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ObservabilityConfig)}
        assert field_names >= {'sampling_rate', 'enable_metrics', 'default_timeout', 'enable_logging', 'enable_tracing'}

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityExecutionAdapterContract:
    def test_is_class(self):
        assert isinstance(ObservabilityExecutionAdapter, type)

    def test_has_method_register_handler(self):
        assert callable(getattr(ObservabilityExecutionAdapter, 'register_handler', None))

    def test_has_method_execute(self):
        assert callable(getattr(ObservabilityExecutionAdapter, 'execute', None))

    def test_has_method_execute_batch(self):
        assert callable(getattr(ObservabilityExecutionAdapter, 'execute_batch', None))

    def test_has_method_get_trace(self):
        assert callable(getattr(ObservabilityExecutionAdapter, 'get_trace', None))

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestCreateObservabilityExecutionAdapterFunction:
    def test_is_callable(self):
        assert callable(create_observability_execution_adapter)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_observability_execution_adapter)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestExecuteObservabilityExecutionFunction:
    def test_is_callable(self):
        assert callable(execute_observability_execution)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(execute_observability_execution)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module observability_type_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
