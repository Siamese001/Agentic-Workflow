"""ADG contract tests for L3_orchestration/types/execution_phase_signal_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_execution_phase_signal_types_adg")
_emit_applies_guardrail("p0", "test_execution_phase_signal_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_phase_signal_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_execution_phase_signal_types_adg", "state_snapshot")
emit_replay_key("p0", "test_execution_phase_signal_types_adg")
emit_determinism_digest("p0", "test_execution_phase_signal_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.execution_phase_signal_types import (
    ExecutionPhase,
    ExecutionPhaseSignal,
    WorkflowSnapshot,
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
