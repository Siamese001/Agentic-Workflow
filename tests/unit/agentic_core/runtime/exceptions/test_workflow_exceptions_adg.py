"""ADG importability contract for agentic_core/runtime/exceptions/workflow_exceptions.py.

Auto-generated stub - covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_workflow_exceptions.py (no _adg suffix).
"""
from __future__ import annotations

from agentic_core.runtime.exceptions.workflow_exceptions import (
    AgenticWorkflowError,
    ApiError,
    CircuitBreakerOpenError,
    HopExecutionError,
    ValidationError,
)  # noqa: F401


class TestWorkflowExceptionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/exceptions/workflow_exceptions.py must be importable."""

        pass  # Import verified at module level

    def test_agenticworkflowerror_defined(self) -> None:
        assert AgenticWorkflowError is not None

    def test_hopexecutionerror_defined(self) -> None:
        assert HopExecutionError is not None

    def test_validationerror_defined(self) -> None:
        assert ValidationError is not None

    def test_apierror_defined(self) -> None:
        assert ApiError is not None

    def test_circuitbreakeropenerror_defined(self) -> None:
        assert CircuitBreakerOpenError is not None
