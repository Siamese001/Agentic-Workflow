"""Tests for agentic_core.evaluation.metrics.classification module.

Tests ConfusionMatrix, BinaryClassificationMetric, and MultiClassF1Metric.
"""
from __future__ import annotations

import pytest

from agentic_core.evaluation.metrics.classification import (
    BinaryClassificationMetric,
    ConfusionMatrix,
    MultiClassF1Metric,
)


class TestConfusionMatrix:
    """Test ConfusionMatrix dataclass and methods."""

    def test_confusion_matrix_creation(self):
        """Test creating a ConfusionMatrix with basic values."""
        cm = ConfusionMatrix(tp=10, fp=5, tn=80, fn=5)
        assert cm.tp == 10
        assert cm.fp == 5
        assert cm.tn == 80
        assert cm.fn == 5

    def test_precision_calculation(self):
        """Test precision = TP / (TP + FP)."""
        cm = ConfusionMatrix(tp=10, fp=5, tn=80, fn=5)
        expected = 10 / (10 + 5)
        assert cm.precision() == pytest.approx(expected, 0.0001)

    def test_precision_zero_denominator(self):
        """Test precision returns 0.0 when TP + FP = 0."""
        cm = ConfusionMatrix(tp=0, fp=0, tn=100, fn=0)
        assert cm.precision() == 0.0

    def test_recall_calculation(self):
        """Test recall = TP / (TP + FN)."""
        cm = ConfusionMatrix(tp=10, fp=5, tn=80, fn=5)
        expected = 10 / (10 + 5)
        assert cm.recall() == pytest.approx(expected, 0.0001)

    def test_recall_zero_denominator(self):
        """Test recall returns 0.0 when TP + FN = 0."""
        cm = ConfusionMatrix(tp=0, fp=5, tn=80, fn=0)
        assert cm.recall() == 0.0

    def test_f1_calculation(self):
        """Test F1 is harmonic mean of precision and recall."""
        cm = ConfusionMatrix(tp=10, fp=5, tn=80, fn=5)
        p = cm.precision()
        r = cm.recall()
        expected = 2 * p * r / (p + r)
        assert cm.f1() == pytest.approx(expected, 0.0001)

    def test_f1_zero_both(self):
        """Test F1 returns 0.0 when both precision and recall are 0."""
        cm = ConfusionMatrix(tp=0, fp=0, tn=100, fn=10)
        assert cm.f1() == 0.0

    def test_accuracy_calculation(self):
        """Test accuracy = (TP + TN) / total."""
        cm = ConfusionMatrix(tp=10, fp=5, tn=80, fn=5)
        expected = (10 + 80) / 100
        assert cm.accuracy() == pytest.approx(expected, 0.0001)

    def test_accuracy_zero_total(self):
        """Test accuracy returns 0.0 on empty matrix."""
        cm = ConfusionMatrix(tp=0, fp=0, tn=0, fn=0)
        assert cm.accuracy() == 0.0

    def test_total_calculation(self):
        """Test total returns sum of all counts."""
        cm = ConfusionMatrix(tp=10, fp=5, tn=80, fn=5)
        assert cm.total() == 100

    def test_to_dict(self):
        """Test serialization to dictionary."""
        cm = ConfusionMatrix(tp=10, fp=5, tn=80, fn=5, positive_label=1)
        d = cm.to_dict()
        assert d["tp"] == 10
        assert d["fp"] == 5
        assert d["tn"] == 80
        assert d["fn"] == 5
        assert d["positive_label"] == 1
        assert "precision" in d
        assert "recall" in d
        assert "f1" in d
        assert "accuracy" in d


class TestBinaryClassificationMetric:
    """Test BinaryClassificationMetric."""

    def test_default_metric_is_f1(self):
        """Test default metric returns F1 score."""
        metric = BinaryClassificationMetric(positive_label=1)
        prediction = [1, 1, 0, 0, 1]
        ground_truth = [1, 0, 0, 1, 1]
        # TP=2, FP=1, TN=1, FN=1
        result = metric.compute(prediction, ground_truth)
        cm = metric.confusion(prediction, ground_truth)
        expected = cm.f1()
        assert result == pytest.approx(expected, 0.0001)

    def test_precision_metric(self):
        """Test metric configured for precision."""
        metric = BinaryClassificationMetric(positive_label=1, metric="precision")
        prediction = [1, 1, 0, 0, 1]
        ground_truth = [1, 0, 0, 1, 1]
        result = metric.compute(prediction, ground_truth)
        cm = metric.confusion(prediction, ground_truth)
        assert result == pytest.approx(cm.precision(), 0.0001)

    def test_recall_metric(self):
        """Test metric configured for recall."""
        metric = BinaryClassificationMetric(positive_label=1, metric="recall")
        prediction = [1, 1, 0, 0, 1]
        ground_truth = [1, 0, 0, 1, 1]
        result = metric.compute(prediction, ground_truth)
        cm = metric.confusion(prediction, ground_truth)
        assert result == pytest.approx(cm.recall(), 0.0001)

    def test_empty_prediction_returns_zero(self):
        """Test empty input returns 0.0."""
        metric = BinaryClassificationMetric()
        result = metric.compute([], [])
        assert result == 0.0

    def test_invalid_metric_raises(self):
        """Test invalid metric name raises ValueError."""
        with pytest.raises(ValueError, match="metric must be 'f1', 'precision', or 'recall'"):
            BinaryClassificationMetric(metric="invalid")

    def test_name_property(self):
        """Test name property reflects metric configuration."""
        metric = BinaryClassificationMetric(metric="precision")
        assert metric.name == "binary_precision"

    def test_mismatched_lengths_raises(self):
        """Test mismatched prediction/ground_truth lengths raise ValueError."""
        metric = BinaryClassificationMetric()
        with pytest.raises(ValueError, match="prediction length.*!=.*ground_truth length"):
            metric.compute([1, 2], [1])


class TestMultiClassF1Metric:
    """Test MultiClassF1Metric."""

    def test_macro_f1_default(self):
        """Test default macro F1 averaging."""
        metric = MultiClassF1Metric()
        prediction = ["A", "B", "A", "C", "B", "A"]
        ground_truth = ["A", "B", "C", "C", "B", "A"]
        result = metric.compute(prediction, ground_truth)
        assert 0.0 <= result <= 1.0

    def test_micro_f1(self):
        """Test micro-averaged F1."""
        metric = MultiClassF1Metric(averaging="micro")
        prediction = ["A", "B", "A", "C", "B", "A"]
        ground_truth = ["A", "B", "C", "C", "B", "A"]
        result = metric.compute(prediction, ground_truth)
        assert 0.0 <= result <= 1.0

    def test_weighted_f1(self):
        """Test weighted-averaged F1."""
        metric = MultiClassF1Metric(averaging="weighted")
        prediction = ["A", "B", "A", "C", "B", "A"]
        ground_truth = ["A", "B", "C", "C", "B", "A"]
        result = metric.compute(prediction, ground_truth)
        assert 0.0 <= result <= 1.0

    def test_precision_metric_multiclass(self):
        """Test multiclass precision metric."""
        metric = MultiClassF1Metric(metric="precision")
        prediction = ["A", "B", "A", "C", "B", "A"]
        ground_truth = ["A", "B", "C", "C", "B", "A"]
        result = metric.compute(prediction, ground_truth)
        assert 0.0 <= result <= 1.0

    def test_empty_prediction_returns_zero(self):
        """Test empty input returns 0.0."""
        metric = MultiClassF1Metric()
        result = metric.compute([], [])
        assert result == 0.0

    def test_mismatched_lengths_raises(self):
        """Test mismatched lengths raise ValueError."""
        metric = MultiClassF1Metric()
        with pytest.raises(ValueError, match="prediction length.*!=.*ground_truth length"):
            metric.compute(["A", "B"], ["A"])

    def test_invalid_averaging_raises(self):
        """Test invalid averaging mode raises ValueError."""
        with pytest.raises(ValueError, match="averaging must be 'macro', 'micro', or 'weighted'"):
            MultiClassF1Metric(averaging="invalid")

    def test_invalid_metric_raises(self):
        """Test invalid metric name raises ValueError."""
        with pytest.raises(ValueError, match="metric must be 'f1', 'precision', or 'recall'"):
            MultiClassF1Metric(metric="invalid")

    def test_per_class_scores(self):
        """Test per-class scores include precision, recall, f1, support."""
        metric = MultiClassF1Metric()
        prediction = ["A", "B", "A", "C", "B", "A"]
        ground_truth = ["A", "B", "C", "C", "B", "A"]
        scores = metric.per_class_scores(prediction, ground_truth)
        for label in ["A", "B", "C"]:
            assert label in scores
            assert "precision" in scores[label]
            assert "recall" in scores[label]
            assert "f1" in scores[label]
            assert "support" in scores[label]

    def test_name_property(self):
        """Test name property reflects configuration."""
        metric = MultiClassF1Metric(averaging="weighted", metric="precision")
        assert metric.name == "multiclass_precision_weighted"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_perfect_binary_classification(self):
        """Test perfect prediction (100% correct)."""
        metric = BinaryClassificationMetric()
        prediction = [1, 1, 1, 0, 0]
        ground_truth = [1, 1, 1, 0, 0]
        result = metric.compute(prediction, ground_truth)
        assert result == 1.0

    def test_all_wrong_binary_classification(self):
        """Test all predictions wrong."""
        metric = BinaryClassificationMetric()
        prediction = [1, 1, 1, 1, 1]
        ground_truth = [0, 0, 0, 0, 0]
        result = metric.compute(prediction, ground_truth)
        assert result == 0.0

    def test_perfect_multiclass(self):
        """Test perfect multiclass prediction."""
        metric = MultiClassF1Metric()
        prediction = ["A", "B", "C", "A", "B"]
        ground_truth = ["A", "B", "C", "A", "B"]
        result = metric.compute(prediction, ground_truth)
        assert result == 1.0

    def test_single_class_multiclass(self):
        """Test multiclass with only one class present."""
        metric = MultiClassF1Metric()
        prediction = ["A", "A", "A"]
        ground_truth = ["A", "A", "A"]
        result = metric.compute(prediction, ground_truth)
        assert result == 1.0
