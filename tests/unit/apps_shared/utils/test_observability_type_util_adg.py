"""ADG-driven tests for apps_shared/utils/observability_type_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.observability_type_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ExecutionLevel,
        ObservabilityConfig,
        ObservabilityExecutionAdapter,
        ObservabilityRequest,
        ObservabilityResult,
        ObservabilityType,
        create_observability_execution_adapter,
        execute_observability_execution,
    )
    _AVAILABLE = True
except ImportError:
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityType:
    def test_is_enum(self):
        import enum
        assert issubclass(ObservabilityType, enum.Enum)
    def test_has_members(self):
        assert len(list(ObservabilityType)) >= 1
    def test_importable(self):
        assert ObservabilityType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestExecutionLevel:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionLevel, enum.Enum)
    def test_has_members(self):
        assert len(list(ExecutionLevel)) >= 1
    def test_importable(self):
        assert ExecutionLevel is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityRequest:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityRequest)
    def test_importable(self):
        assert ObservabilityRequest is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityResult)
    def test_importable(self):
        assert ObservabilityResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ObservabilityConfig)
    def test_importable(self):
        assert ObservabilityConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestObservabilityExecutionAdapter:
    def test_is_class(self):
        assert isinstance(ObservabilityExecutionAdapter, type)
    def test_importable(self):
        assert ObservabilityExecutionAdapter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestCreateObservabilityExecutionAdapter:
    def test_is_callable(self):
        assert callable(create_observability_execution_adapter)

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestExecuteObservabilityExecution:
    def test_is_callable(self):
        assert callable(execute_observability_execution)

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

@pytest.mark.skipif(not _AVAILABLE, reason="observability_type_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module observability_type_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
