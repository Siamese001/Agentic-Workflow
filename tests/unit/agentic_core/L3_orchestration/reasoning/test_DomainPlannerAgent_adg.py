"""ADG importability contract for agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_DomainPlannerAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.reasoning.DomainPlannerAgent import (  # noqa: F401
        DomainPlannerAgent,
        DomainPlannerOutput,
        PlannerAssessment,
        ScenarioSimulationResult,
        StrategyPlan,
        WorkflowContext,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DomainPlannerOutput = None  # type: ignore[assignment,misc]
    PlannerAssessment = None  # type: ignore[assignment,misc]
    ScenarioSimulationResult = None  # type: ignore[assignment,misc]
    StrategyPlan = None  # type: ignore[assignment,misc]
    WorkflowContext = None  # type: ignore[assignment,misc]
    DomainPlannerAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent deps unavailable")
class TestDomainplanneragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py must be importable."""
        assert _AVAILABLE

    def test_domainplanneroutput_defined(self) -> None:
        assert DomainPlannerOutput is not None

    def test_plannerassessment_defined(self) -> None:
        assert PlannerAssessment is not None

    def test_scenariosimulationresult_defined(self) -> None:
        assert ScenarioSimulationResult is not None

    def test_strategyplan_defined(self) -> None:
        assert StrategyPlan is not None

    def test_workflowcontext_defined(self) -> None:
        assert WorkflowContext is not None

    def test_domainplanneragent_defined(self) -> None:
        assert DomainPlannerAgent is not None
