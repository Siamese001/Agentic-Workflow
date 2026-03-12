"""ADG-driven tests for L2_execution/engines/action_node.py — fan_in=0."""
from __future__ import annotations

import pytest

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
