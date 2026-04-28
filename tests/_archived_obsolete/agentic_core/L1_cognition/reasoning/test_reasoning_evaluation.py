"""Tests for reasoning_evaluation - reasoning output evaluation."""
import pytest
from agentic_core.L1_cognition.reasoning.reasoning_evaluation import ReasoningEvaluator


class TestReasoningEvaluator:
    def test_init(self):
        e = ReasoningEvaluator()
        assert e is not None

    def test_evaluate_correct_output(self):
        e = ReasoningEvaluator()
        result = e.evaluate(output="2+2=4", expected="2+2=4")
        assert result.score >= 0.9

    def test_evaluate_incorrect_output(self):
        e = ReasoningEvaluator()
        result = e.evaluate(output="2+2=5", expected="2+2=4")
        assert result.score < 0.5

    def test_evaluate_with_rubric(self):
        e = ReasoningEvaluator()
        rubric = {"clarity": 0.5, "correctness": 0.5}
        result = e.evaluate_with_rubric(output="x", rubric=rubric)
        assert hasattr(result, "score")

    def test_batch_evaluate(self):
        e = ReasoningEvaluator()
        outputs = [{"o": "a", "e": "a"}, {"o": "b", "e": "c"}]
        results = e.batch_evaluate(outputs)
        assert len(results) == 2

    def test_empty_output(self):
        e = ReasoningEvaluator()
        result = e.evaluate(output="", expected="x")
        assert result.score == 0.0
