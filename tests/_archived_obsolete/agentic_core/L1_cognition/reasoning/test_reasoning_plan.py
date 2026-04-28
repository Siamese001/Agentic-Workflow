"""Tests for reasoning_plan - reasoning plan construction and execution."""
import pytest
from agentic_core.L1_cognition.reasoning.reasoning_plan import ReasoningPlan


class TestReasoningPlan:
    def test_init(self):
        p = ReasoningPlan(goal="solve x")
        assert p.goal == "solve x"

    def test_add_step(self):
        p = ReasoningPlan(goal="x")
        p.add_step({"action": "analyze"})
        assert len(p.steps) == 1

    def test_remove_step(self):
        p = ReasoningPlan(goal="x")
        p.add_step({"id": "1", "action": "a"})
        p.remove_step("1")
        assert len(p.steps) == 0

    def test_get_step(self):
        p = ReasoningPlan(goal="x")
        p.add_step({"id": "1", "action": "a"})
        s = p.get_step("1")
        assert s["action"] == "a"

    def test_validate_plan(self):
        p = ReasoningPlan(goal="x")
        p.add_step({"id": "1", "action": "a"})
        assert p.validate() is True

    def test_invalid_empty_plan(self):
        p = ReasoningPlan(goal="x")
        assert p.validate() is False

    def test_serialize(self):
        p = ReasoningPlan(goal="x")
        p.add_step({"id": "1", "action": "a"})
        data = p.to_dict()
        assert "goal" in data and "steps" in data
