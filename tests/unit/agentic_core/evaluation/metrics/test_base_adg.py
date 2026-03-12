"""ADG-driven tests for evaluation/metrics/base.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.evaluation.metrics.base import EvaluationMetric, RetrievalMetric


class TestEvaluationMetric:
    def test_is_abstract(self):
        import inspect
        assert inspect.isabstract(EvaluationMetric)

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            EvaluationMetric()

    def test_subclass_requires_name_and_compute(self):
        class Concrete(EvaluationMetric):
            @property
            def name(self) -> str:
                return "test"

            def compute(self, prediction, ground_truth, context=None) -> float:
                return 1.0

        m = Concrete()
        assert m.name == "test"
        assert m.compute("a", "b") == pytest.approx(1.0)


class TestRetrievalMetric:
    def test_is_abstract(self):
        import inspect
        assert inspect.isabstract(RetrievalMetric)

    def test_is_subclass_of_evaluation_metric(self):
        assert issubclass(RetrievalMetric, EvaluationMetric)
