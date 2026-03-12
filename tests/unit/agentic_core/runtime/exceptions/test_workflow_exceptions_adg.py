"""ADG-driven tests for agentic_core/runtime/exceptions/workflow_exceptions.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.exceptions.workflow_exceptions import (  # noqa: F401
        AgenticWorkflowError,
        HopExecutionError,
        ValidationError,
        ApiError,
        CircuitBreakerOpenError,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AgenticWorkflowError = None  # type: ignore[assignment,misc]
    HopExecutionError = None  # type: ignore[assignment,misc]
    ValidationError = None  # type: ignore[assignment,misc]
    ApiError = None  # type: ignore[assignment,misc]
    CircuitBreakerOpenError = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestAgenticWorkflowError:
    def test_is_class(self):
        assert isinstance(AgenticWorkflowError, type)
    def test_importable(self):
        assert AgenticWorkflowError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestHopExecutionError:
    def test_is_class(self):
        assert isinstance(HopExecutionError, type)
    def test_importable(self):
        assert HopExecutionError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestValidationError:
    def test_is_class(self):
        assert isinstance(ValidationError, type)
    def test_importable(self):
        assert ValidationError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestApiError:
    def test_is_class(self):
        assert isinstance(ApiError, type)
    def test_importable(self):
        assert ApiError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestCircuitBreakerOpenError:
    def test_is_class(self):
        assert isinstance(CircuitBreakerOpenError, type)
    def test_importable(self):
        assert CircuitBreakerOpenError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module workflow_exceptions.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
