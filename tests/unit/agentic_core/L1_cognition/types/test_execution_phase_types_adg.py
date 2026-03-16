"""ADG-driven tests for L1_cognition/types/execution_phase_types.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_execution_phase_types_adg")
_emit_applies_guardrail("p0", "test_execution_phase_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_phase_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_execution_phase_types_adg", "state_snapshot")
emit_replay_key("p0", "test_execution_phase_types_adg")
emit_determinism_digest("p0", "test_execution_phase_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.execution_phase_types import (
    ExecutionContext,
    ExecutionPhase,
)


class TestExecutionPhase:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionPhase, enum.Enum)

    def test_think_value(self):
        assert ExecutionPhase.THINK.value == "think"

    def test_act_value(self):
        assert ExecutionPhase.ACT.value == "act"

    def test_all_values_are_strings(self):
        for phase in ExecutionPhase:
            assert isinstance(phase.value, str)


class TestExecutionContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionContext)

    def test_creates_with_defaults(self):
        ctx = ExecutionContext(mission="build a feature")
        assert ctx.mission == "build a feature"
        assert ctx.scene == {}
        assert ctx.history == []
