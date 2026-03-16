"""ADG-driven tests for L5_safety/reasoning/NeuralAutoImmuneAgent.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_neural_auto_immune_agent_adg")
_emit_applies_guardrail("p0", "test_neural_auto_immune_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_neural_auto_immune_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_neural_auto_immune_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_neural_auto_immune_agent_adg")
emit_determinism_digest("p0", "test_neural_auto_immune_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.NeuralAutoImmuneAgent import NeuralAutoImmuneAgent


class TestNeuralAutoImmuneAgent:
    def test_creates(self):
        agent = NeuralAutoImmuneAgent()
        assert agent is not None

    def test_has_heal(self):
        assert hasattr(NeuralAutoImmuneAgent, "heal")

    def test_has_heal_repository(self):
        assert hasattr(NeuralAutoImmuneAgent, "heal_repository")

    def test_heal_returns_dict(self):
        agent = NeuralAutoImmuneAgent()
        result = agent.heal({"type": "test", "file": "foo.py"})
        assert isinstance(result, dict)
        assert "status" in result
