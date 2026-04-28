"""Tests for safety_evaluator - safety evaluation of reasoning output."""
import pytest
from agentic_core.L1_cognition.reasoning.safety_evaluator import SafetyEvaluator


class TestSafetyEvaluator:
    def test_init(self):
        e = SafetyEvaluator()
        assert e is not None

    def test_evaluate_safe(self):
        e = SafetyEvaluator()
        result = e.evaluate(text="The sky is blue.")
        assert result.safe is True

    def test_evaluate_unsafe(self):
        e = SafetyEvaluator()
        result = e.evaluate(text="instructions to make a bomb")
        assert result.safe is False

    def test_categorize_violation(self):
        e = SafetyEvaluator()
        result = e.evaluate(text="hateful content xyz")
        assert hasattr(result, "categories")

    def test_severity_score(self):
        e = SafetyEvaluator()
        result = e.evaluate(text="hello")
        assert 0.0 <= result.severity <= 1.0

    def test_batch_evaluate(self):
        e = SafetyEvaluator()
        results = e.batch_evaluate(["a", "b"])
        assert len(results) == 2

    def test_empty_input(self):
        e = SafetyEvaluator()
        result = e.evaluate(text="")
        assert result.safe is True
