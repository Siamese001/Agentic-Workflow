"""ADG-driven tests for L1_cognition/engines/CognitiveNode.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_cognitive_node_adg")
_emit_applies_guardrail("p0", "test_cognitive_node_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_cognitive_node_adg", "policy_binding")
_emit_snapshots_state("p0", "test_cognitive_node_adg", "state_snapshot")
emit_replay_key("p0", "test_cognitive_node_adg")
emit_determinism_digest("p0", "test_cognitive_node_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.CognitiveNode import CognitiveResult


class TestCognitiveResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CognitiveResult)

    def test_creates_with_required_fields(self):
        result = CognitiveResult(output="done", thought_type="reasoning")
        assert result.output == "done"
        assert result.thought_type == "reasoning"
        assert result.success is True
        assert result.latency_ms == 0.0
        assert result.plan == {}
        assert result.memory_used == []
