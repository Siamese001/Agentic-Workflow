"""ADG contract tests for L3_orchestration/types/execution_phase_signal_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.execution_phase_signal_types import (
    ExecutionPhaseSignal, ExecutionPhase, WorkflowSnapshot,
)

class TestExecutionPhaseSignal:
    def test_is_enum(self):
        import enum; assert issubclass(ExecutionPhaseSignal, enum.Enum)
    def test_has_four_phases(self): assert len(list(ExecutionPhaseSignal)) == 4

class TestExecutionPhase:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ExecutionPhase)
    def test_creates(self):
        p = ExecutionPhase(name="planning", agents=["a1"])
        assert p.name == "planning"
    def test_signal_auto_set(self):
        p = ExecutionPhase(name="execution", agents=[])
        assert p.signal == ExecutionPhaseSignal.EXECUTION

class TestWorkflowSnapshot:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(WorkflowSnapshot)
    def test_creates(self):
        s = WorkflowSnapshot(cycle=1, context={}, outputs={})
        assert s.cycle == 1
