"""
F1Score — public binary F1 metric.

Thin wrapper around BinaryClassificationMetric that always returns the F1
harmonic mean.  This is the canonical public API for binary classification F1.

Usage:
    from agentic_core.evaluation.metrics.f1_score import F1Score

    metric = F1Score(positive_label=1)
    score = metric.compute(predictions, ground_truth)   # float in [0, 1]
    cm = metric.confusion(predictions, ground_truth)    # ConfusionMatrix
"""

from __future__ import annotations

from typing import Any

from agentic_core.evaluation.metrics.classification import BinaryClassificationMetric, ConfusionMatrix


class F1Score(BinaryClassificationMetric):
    """Binary F1 score: harmonic mean of precision and recall.

    ``F1 = 2 * precision * recall / (precision + recall)``

    Args:
        positive_label: The label treated as the positive class (default 1).
    """

    def __init__(self, positive_label: Any = 1) -> None:
        super().__init__(positive_label=positive_label, metric="f1")

    @property
    def name(self) -> str:
        return "f1_score"

    def compute(self, prediction: list, ground_truth: list, context: Any = None) -> float:
        """Compute binary F1 score.

        Args:
            prediction: Flat list of predicted labels.
            ground_truth: Flat list of true labels (same length).
            context: Unused.

        Returns:
            F1 score in [0.0, 1.0].
        """
        return super().compute(prediction, ground_truth, context)

    def confusion(self, prediction: list, ground_truth: list) -> ConfusionMatrix:
        """Return ConfusionMatrix for the given predictions."""
        return super().confusion(prediction, ground_truth)


__all__ = ["F1Score"]
