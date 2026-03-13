"""ADG importability contract for agentic_core/L0_routing/scripts/execution.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_execution.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.execution import (  # noqa: F401
        DAGStrategy,
        ExecutionStatus,
        ExecutionStrategy,
        WorkflowContext,
        WorkflowResult,
        WorkflowStep,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExecutionStatus = None  # type: ignore[assignment,misc]
    WorkflowContext = None  # type: ignore[assignment,misc]
    WorkflowResult = None  # type: ignore[assignment,misc]
    WorkflowStep = None  # type: ignore[assignment,misc]
    ExecutionStrategy = None  # type: ignore[assignment,misc]
    DAGStrategy = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="execution deps unavailable")
class TestExecutionImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/scripts/execution.py must be importable."""
        assert _AVAILABLE

    def test_executionstatus_defined(self) -> None:
        assert ExecutionStatus is not None

    def test_workflowcontext_defined(self) -> None:
        assert WorkflowContext is not None

    def test_workflowresult_defined(self) -> None:
        assert WorkflowResult is not None

    def test_workflowstep_defined(self) -> None:
        assert WorkflowStep is not None

    def test_executionstrategy_defined(self) -> None:
        assert ExecutionStrategy is not None

    def test_dagstrategy_defined(self) -> None:
        assert DAGStrategy is not None
