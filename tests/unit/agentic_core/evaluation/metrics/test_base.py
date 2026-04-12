"""Tests for agentic_core.evaluation.base module.

Tests EvaluationMetric abstract base classes.
"""

from __future__ import annotations

import pytest

from agentic_core.evaluation.metrics.base import (
    ClassificationMetric,
    EvaluationMetric,
    GenerationMetric,
    RetrievalMetric,
)
from agentic_core.evaluation.metrics.classification import ConfusionMatrix


class ConcreteEvaluationMetric(EvaluationMetric):
    """Concrete implementation for testing."""

    @property
    def name(self) -> str:
        return "test_metric"

    def compute(self, prediction: object, ground_truth: object, context: object = None) -> float:
        return 1.0 if prediction == ground_truth else 0.0


class ConcreteRetrievalMetric(RetrievalMetric):
    """Concrete retrieval metric for testing."""

    @property
    def name(self) -> str:
        return "test_retrieval"

    def compute(
        self,
        prediction: list[str],
        ground_truth: list[str],
        context: object = None,
    ) -> float:
        if not prediction or not ground_truth:
            return 0.0
        # Simple overlap calculation
        pred_set = set(prediction)
        gt_set = set(ground_truth)
        overlap = len(pred_set & gt_set)
        return overlap / len(gt_set) if gt_set else 0.0


class ConcreteGenerationMetric(GenerationMetric):
    """Concrete generation metric for testing."""

    @property
    def name(self) -> str:
        return "test_generation"

    def compute(self, prediction: str, ground_truth: str, context: object = None) -> float:
        # Simple exact match
        return 1.0 if prediction.strip() == ground_truth.strip() else 0.0


class ConcreteClassificationMetric(ClassificationMetric):
    """Concrete classification metric for testing."""

    @property
    def name(self) -> str:
        return "test_classification"

    def compute(self, prediction: list, ground_truth: list, context: object = None) -> float:
        if not prediction or not ground_truth:
            return 0.0
        correct = sum(1 for p, g in zip(prediction, ground_truth) if p == g)
        return correct / len(ground_truth)

    def confusion(
        self,
        prediction: list,
        ground_truth: list,
    ) -> ConfusionMatrix:
        tp = sum(1 for p, g in zip(prediction, ground_truth) if p == g == 1)
        fp = sum(1 for p, g in zip(prediction, ground_truth) if p == 1 and g == 0)
        tn = sum(1 for p, g in zip(prediction, ground_truth) if p == g == 0)
        fn = sum(1 for p, g in zip(prediction, ground_truth) if p == 0 and g == 1)
        return ConfusionMatrix(tp=tp, fp=fp, tn=tn, fn=fn)


class TestEvaluationMetric:
    """Test EvaluationMetric base class."""

    def test_concrete_metric_can_be_instantiated(self):
        """Test concrete implementation can be created."""
        metric = ConcreteEvaluationMetric()
        assert metric.name == "test_metric"

    def test_concrete_metric_compute(self):
        """Test compute method returns score."""
        metric = ConcreteEvaluationMetric()
        result = metric.compute("hello", "hello")
        assert result == 1.0

    def test_concrete_metric_compute_mismatch(self):
        """Test compute with mismatched inputs."""
        metric = ConcreteEvaluationMetric()
        result = metric.compute("hello", "world")
        assert result == 0.0

    def test_abstract_class_cannot_be_instantiated(self):
        """Test EvaluationMetric is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            EvaluationMetric()  # type: ignore[abstract]


class TestRetrievalMetric:
    """Test RetrievalMetric base class."""

    def test_retrieval_metric_name(self):
        """Test retrieval metric has name."""
        metric = ConcreteRetrievalMetric()
        assert metric.name == "test_retrieval"

    def test_retrieval_compute_with_overlap(self):
        """Test compute with overlapping results."""
        metric = ConcreteRetrievalMetric()
        prediction = ["doc1", "doc2", "doc3"]
        ground_truth = ["doc1", "doc4"]
        result = metric.compute(prediction, ground_truth)
        assert result == 0.5  # 1 out of 2 retrieved

    def test_retrieval_compute_no_overlap(self):
        """Test compute with no overlap."""
        metric = ConcreteRetrievalMetric()
        prediction = ["doc1", "doc2"]
        ground_truth = ["doc3", "doc4"]
        result = metric.compute(prediction, ground_truth)
        assert result == 0.0

    def test_retrieval_compute_empty(self):
        """Test compute with empty lists."""
        metric = ConcreteRetrievalMetric()
        result = metric.compute([], ["doc1"])
        assert result == 0.0


class TestGenerationMetric:
    """Test GenerationMetric base class."""

    def test_generation_metric_name(self):
        """Test generation metric has name."""
        metric = ConcreteGenerationMetric()
        assert metric.name == "test_generation"

    def test_generation_compute_exact_match(self):
        """Test compute with exact match."""
        metric = ConcreteGenerationMetric()
        result = metric.compute("Hello world", "Hello world")
        assert result == 1.0

    def test_generation_compute_no_match(self):
        """Test compute with no match."""
        metric = ConcreteGenerationMetric()
        result = metric.compute("Hello", "World")
        assert result == 0.0

    def test_generation_compute_with_whitespace(self):
        """Test compute handles whitespace stripping."""
        metric = ConcreteGenerationMetric()
        result = metric.compute("  Hello  ", "Hello")
        assert result == 1.0


class TestClassificationMetric:
    """Test ClassificationMetric base class."""

    def test_classification_metric_name(self):
        """Test classification metric has name."""
        metric = ConcreteClassificationMetric()
        assert metric.name == "test_classification"

    def test_classification_compute(self):
        """Test compute method."""
        metric = ConcreteClassificationMetric()
        prediction = [1, 0, 1, 1]
        ground_truth = [1, 0, 0, 1]
        result = metric.compute(prediction, ground_truth)
        assert result == 0.75  # 3 out of 4 correct

    def test_classification_compute_perfect(self):
        """Test compute with perfect predictions."""
        metric = ConcreteClassificationMetric()
        prediction = [1, 0, 1, 0]
        ground_truth = [1, 0, 1, 0]
        result = metric.compute(prediction, ground_truth)
        assert result == 1.0

    def test_classification_confusion(self):
        """Test confusion matrix generation."""
        metric = ConcreteClassificationMetric()
        prediction = [1, 0, 1, 1]
        ground_truth = [1, 0, 0, 1]
        cm = metric.confusion(prediction, ground_truth)
        assert cm.tp == 2  # Positions 0 and 3
        assert cm.fp == 1  # Position 2 (predicted 1, actual 0)
        assert cm.tn == 1  # Position 1
        assert cm.fn == 0


class TestAbstractClassEnforcement:
    """Test that abstract methods must be implemented."""

    def test_retrieval_metric_requires_compute(self):
        """Test RetrievalMetric requires compute implementation."""

        class IncompleteRetrievalMetric(RetrievalMetric):
            @property
            def name(self) -> str:
                return "incomplete"

        with pytest.raises(TypeError):
            IncompleteRetrievalMetric()  # type: ignore[abstract]

    def test_generation_metric_requires_compute(self):
        """Test GenerationMetric requires compute implementation."""

        class IncompleteGenerationMetric(GenerationMetric):
            @property
            def name(self) -> str:
                return "incomplete"

        with pytest.raises(TypeError):
            IncompleteGenerationMetric()  # type: ignore[abstract]

    def test_classification_metric_requires_both_methods(self):
        """Test ClassificationMetric requires both compute and confusion."""

        class IncompleteClassificationMetric(ClassificationMetric):
            @property
            def name(self) -> str:
                return "incomplete"

            def compute(self, prediction: list, ground_truth: list, context: object = None) -> float:
                return 0.0

        with pytest.raises(TypeError):
            IncompleteClassificationMetric()  # type: ignore[abstract]
