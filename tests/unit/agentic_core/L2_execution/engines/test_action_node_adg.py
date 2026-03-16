"""ADG-driven tests for L2_execution/engines/action_node.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_action_node_adg")
_emit_applies_guardrail("p0", "test_action_node_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_action_node_adg", "policy_binding")
_emit_snapshots_state("p0", "test_action_node_adg", "state_snapshot")
emit_replay_key("p0", "test_action_node_adg")
emit_determinism_digest("p0", "test_action_node_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.engines.action_node import ActionNode


class TestActionNode:
    def test_creates(self):
        node = ActionNode()
        assert node.actions_executed == 0
        assert node.tools_used == 0
        assert node.total_execution_time == 0.0

    def test_has_act_method(self):
        assert callable(getattr(ActionNode, "act", None))

    def test_act_returns_dict(self):
        node = ActionNode()
        result = node.act({"plan": {"steps": []}, "tool": "file", "action": "read"})
        assert isinstance(result, dict)
