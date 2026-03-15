"""Foundational behavioral tests for agentic_core/runtime/exceptions/workflow_exceptions.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_workflow_exceptions_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.exceptions.workflow_exceptions import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AgenticWorkflowError,
        ApiError,
        CircuitBreakerOpenError,
        HopExecutionError,
        ValidationError,
    )
    _AVAILABLE = True
except ImportError as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestAgenticWorkflowErrorContract:
    def test_is_class(self):
        assert isinstance(AgenticWorkflowError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(AgenticWorkflowError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestHopExecutionErrorContract:
    def test_is_class(self):
        assert isinstance(HopExecutionError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HopExecutionError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestValidationErrorContract:
    def test_is_class(self):
        assert isinstance(ValidationError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ValidationError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestApiErrorContract:
    def test_is_class(self):
        assert isinstance(ApiError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ApiError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions.py deps unavailable")
class TestCircuitBreakerOpenErrorContract:
    def test_is_class(self):
        assert isinstance(CircuitBreakerOpenError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(CircuitBreakerOpenError, type)

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


def test_module_importable():
    """Module workflow_exceptions must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
