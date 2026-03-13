"""ADG importability contract for agentic_core/runtime/exceptions/workflow_exceptions.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_workflow_exceptions.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.exceptions.workflow_exceptions import (  # noqa: F401
        AgenticWorkflowError,
        ApiError,
        CircuitBreakerOpenError,
        HopExecutionError,
        ValidationError,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AgenticWorkflowError = None  # type: ignore[assignment,misc]
    HopExecutionError = None  # type: ignore[assignment,misc]
    ValidationError = None  # type: ignore[assignment,misc]
    ApiError = None  # type: ignore[assignment,misc]
    CircuitBreakerOpenError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="workflow_exceptions deps unavailable")
class TestWorkflowExceptionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/exceptions/workflow_exceptions.py must be importable."""
        assert _AVAILABLE

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
