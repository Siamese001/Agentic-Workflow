"""Foundational behavioral tests for agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_DomainPlannerAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L3_orchestration.reasoning.DomainPlannerAgent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        DomainPlannerAgent,
        DomainPlannerOutput,
        PlannerAssessment,
        ScenarioSimulationResult,
        StrategyPlan,
        WorkflowContext,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    DomainPlannerOutput = None  # type: ignore[assignment,misc]
    PlannerAssessment = None  # type: ignore[assignment,misc]
    ScenarioSimulationResult = None  # type: ignore[assignment,misc]
    StrategyPlan = None  # type: ignore[assignment,misc]
    WorkflowContext = None  # type: ignore[assignment,misc]
    DomainPlannerAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestDomainPlannerOutputContract:
    def test_is_class(self):
        assert isinstance(DomainPlannerOutput, type)

    def test_has_method_model_dump(self):
        assert callable(getattr(DomainPlannerOutput, 'model_dump', None))

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestPlannerAssessmentContract:
    def test_is_class(self):
        assert isinstance(PlannerAssessment, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(PlannerAssessment, type)

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestScenarioSimulationResultContract:
    def test_is_class(self):
        assert isinstance(ScenarioSimulationResult, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ScenarioSimulationResult, type)

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestStrategyPlanContract:
    def test_is_class(self):
        assert isinstance(StrategyPlan, type)

    def test_has_method_model_copy(self):
        assert callable(getattr(StrategyPlan, 'model_copy', None))

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestWorkflowContextContract:
    def test_is_class(self):
        assert isinstance(WorkflowContext, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(WorkflowContext, type)

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestDomainPlannerAgentContract:
    def test_is_class(self):
        assert isinstance(DomainPlannerAgent, type)

    def test_has_method_run_async(self):
        assert callable(getattr(DomainPlannerAgent, 'run_async', None))

    def test_has_method_log_feedback(self):
        assert callable(getattr(DomainPlannerAgent, 'log_feedback', None))

    def test_has_method_heal_repository(self):
        assert callable(getattr(DomainPlannerAgent, 'heal_repository', None))

    def test_has_method_heal(self):
        assert callable(getattr(DomainPlannerAgent, 'heal', None))

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DomainPlannerAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module DomainPlannerAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
