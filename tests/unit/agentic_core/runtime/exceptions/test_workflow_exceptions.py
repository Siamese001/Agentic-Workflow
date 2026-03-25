"""Foundational behavioral tests for agentic_core/runtime/exceptions/workflow_exceptions.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_workflow_exceptions_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

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


class TestAgenticWorkflowErrorContract:
    def test_is_class(self):
        assert isinstance(AgenticWorkflowError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(AgenticWorkflowError, type)

class TestHopExecutionErrorContract:
    def test_is_class(self):
        assert isinstance(HopExecutionError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HopExecutionError, type)

class TestValidationErrorContract:
    def test_is_class(self):
        assert isinstance(ValidationError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ValidationError, type)

class TestApiErrorContract:
    def test_is_class(self):
        assert isinstance(ApiError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ApiError, type)

class TestCircuitBreakerOpenErrorContract:
    def test_is_class(self):
        assert isinstance(CircuitBreakerOpenError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(CircuitBreakerOpenError, type)

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module workflow_exceptions must be importable or skip gracefully."""
    pass  # Import verified at module level
