"""ADG-driven tests for L1_cognition/config/react_config.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_react_config_adg")
_emit_applies_guardrail("p0", "test_react_config_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_react_config_adg", "policy_binding")
_emit_snapshots_state("p0", "test_react_config_adg", "state_snapshot")
emit_replay_key("p0", "test_react_config_adg")
emit_determinism_digest("p0", "test_react_config_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.config.react_config import (
    ReActStep,
    ReasoningMode,
)


class TestReasoningMode:
    def test_is_enum(self):
        import enum
        assert issubclass(ReasoningMode, enum.Enum)

    def test_react_value(self):
        assert ReasoningMode.REACT.value == "react"

    def test_chain_of_thought_value(self):
        assert ReasoningMode.CHAIN_OF_THOUGHT.value == "cot"

    def test_all_values_are_strings(self):
        for mode in ReasoningMode:
            assert isinstance(mode.value, str)


class TestReActStep:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ReActStep)

    def test_creates(self):
        step = ReActStep(step_number=1, thought="analyze this", action="search")
        assert step.step_number == 1
        assert step.thought == "analyze this"
        assert step.action == "search"
        assert step.observation == ""
