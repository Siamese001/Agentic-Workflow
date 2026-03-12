"""ADG-driven tests for L1_cognition/validators/reasoningnode_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.reasoningnode_validator import ReasoningNode


class TestReasoningNode:
    def test_creates(self):
        node = ReasoningNode()
        assert node.thoughts_generated == 0
        assert node.plans_created == 0
        assert node.total_reasoning_time == 0.0

    def test_has_reason(self):
        assert hasattr(ReasoningNode, "reason")

    def test_reason_returns_dict(self):
        node = ReasoningNode()
        result = node.reason({"query": "analyze this", "intent": "task"})
        assert isinstance(result, dict)
