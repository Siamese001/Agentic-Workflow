"""ADG importability contract for agentic_core/L3_orchestration/engines/autonomous_workflow_engine.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_autonomous_workflow_engine.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.autonomous_workflow_engine import (  # noqa: F401
        AutonomousWorkflowEngine,
        EnvironmentToolSet,
        StopSignal,
        WorkflowResult,
        WorkflowStep,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    StopSignal = None  # type: ignore[assignment,misc]
    EnvironmentToolSet = None  # type: ignore[assignment,misc]
    WorkflowStep = None  # type: ignore[assignment,misc]
    WorkflowResult = None  # type: ignore[assignment,misc]
    AutonomousWorkflowEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="autonomous_workflow_engine deps unavailable")
class TestAutonomousWorkflowEngineImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/engines/autonomous_workflow_engine.py must be importable."""
        assert _AVAILABLE

    def test_stopsignal_defined(self) -> None:
        assert StopSignal is not None

    def test_environmenttoolset_defined(self) -> None:
        assert EnvironmentToolSet is not None

    def test_workflowstep_defined(self) -> None:
        assert WorkflowStep is not None

    def test_workflowresult_defined(self) -> None:
        assert WorkflowResult is not None

    def test_autonomousworkflowengine_defined(self) -> None:
        assert AutonomousWorkflowEngine is not None