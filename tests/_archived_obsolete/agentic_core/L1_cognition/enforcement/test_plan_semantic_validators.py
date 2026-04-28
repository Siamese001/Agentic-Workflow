"""Tests for plan_semantic_validators - plan validation logic."""
import pytest
from agentic_core.L1_cognition.enforcement import plan_semantic_validators as psv


class TestPlanSemanticValidators:
    def test_validate_plan_structure(self):
        plan = {"goal": "x", "steps": [{"action": "a"}]}
        result = psv.validate_plan_structure(plan)
        assert result.valid is True

    def test_invalid_missing_goal(self):
        plan = {"steps": []}
        result = psv.validate_plan_structure(plan)
        assert result.valid is False

    def test_invalid_no_steps(self):
        plan = {"goal": "x", "steps": []}
        result = psv.validate_plan_structure(plan)
        assert result.valid is False

    def test_validate_step_dependencies(self):
        plan = {
            "goal": "x",
            "steps": [
                {"id": "1", "action": "a"},
                {"id": "2", "action": "b", "depends_on": ["1"]}
            ]
        }
        result = psv.validate_dependencies(plan)
        assert result.valid is True

    def test_invalid_circular_deps(self):
        plan = {
            "goal": "x",
            "steps": [
                {"id": "1", "depends_on": ["2"]},
                {"id": "2", "depends_on": ["1"]}
            ]
        }
        result = psv.validate_dependencies(plan)
        assert result.valid is False

    def test_validate_estimated_tokens(self):
        plan = {"goal": "x", "estimated_tokens": 1000, "steps": [{"action": "a"}]}
        result = psv.validate_token_budget(plan, max_tokens=10000)
        assert result.valid is True

    def test_invalid_token_overflow(self):
        plan = {"goal": "x", "estimated_tokens": 100000, "steps": [{"action": "a"}]}
        result = psv.validate_token_budget(plan, max_tokens=10000)
        assert result.valid is False
