"""
Classification Metrics: ConfusionMatrix, BinaryClassificationMetric, MultiClassF1Metric.

Deterministic, pure-Python, zero external dependencies.

Hierarchy:
    ClassificationMetric (ABC, base.py)
    ├── BinaryClassificationMetric   - binary labels, TP/FP/TN/FN
    └── MultiClassF1Metric           - per-class F1 + macro/micro/weighted averaging
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal

from .base import ClassificationMetric

try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        LayerSegment,
        _emit_records_execution_trace,
    )
except ModuleNotFoundError:

    class LayerSegment:
        L3_ORCHESTRATION = "L3_ORCHESTRATION"

    def _emit_records_execution_trace(*args: Any, **kwargs: Any) -> None:
        return None


def _trace_id(operation: str, payload: str) -> str:
    """Stable trace ID so metrics remain replay-friendly."""
    return hashlib.sha256(f"{operation}|{payload}".encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class ConfusionMatrix:
    """Immutable binary confusion matrix counts.

    Attributes:
        tp: True positives
        fp: False positives
        tn: True negatives
        fn: False negatives
        positive_label: The label treated as the positive class
    """

    tp: int
    fp: int
    tn: int
    fn: int
    positive_label: Any = 1

    def precision(self) -> float:
        """TP / (TP + FP). Returns 0.0 when denominator is zero."""
        trace_id = _trace_id(
            "ConfusionMatrix.precision",
            f"{self.tp}|{self.fp}|{self.tn}|{self.fn}|{self.positive_label}",
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "ConfusionMatrix.precision",
        )

        denom = self.tp + self.fp
        return round(self.tp / denom, 6) if denom > 0 else 0.0

    def recall(self) -> float:
        """TP / (TP + FN). Returns 0.0 when denominator is zero."""
        denom = self.tp + self.fn
        return round(self.tp / denom, 6) if denom > 0 else 0.0

    def f1(self) -> float:
        """Harmonic mean of precision and recall. Returns 0.0 when both are 0."""
        p = self.precision()
        r = self.recall()
        denom = p + r
        return round(2 * p * r / denom, 6) if denom > 0.0 else 0.0

    def accuracy(self) -> float:
        """(TP + TN) / total. Returns 0.0 on empty input."""
        total = self.tp + self.fp + self.tn + self.fn
        return round((self.tp + self.tn) / total, 6) if total > 0 else 0.0

    def total(self) -> int:
        """Total number of samples."""
        return self.tp + self.fp + self.tn + self.fn

    def to_dict(self) -> dict[str, Any]:
        return {
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
            "positive_label": self.positive_label,
            "precision": self.precision(),
            "recall": self.recall(),
            "f1": self.f1(),
            "accuracy": self.accuracy(),
        }


# ---------------------------------------------------------------------------
# BinaryClassificationMetric
# ---------------------------------------------------------------------------


def _build_binary_confusion(
    prediction: list,
    ground_truth: list,
    positive_label: Any,
) -> ConfusionMatrix:
    """Compute binary confusion matrix from parallel label lists."""
    if len(prediction) != len(ground_truth):
        raise ValueError(f"prediction length {len(prediction)} != ground_truth length {len(ground_truth)}")
    tp = fp = tn = fn = 0
    for pred, true in zip(prediction, ground_truth):  # progress_bar: compute confusion matrix
        pred_pos = pred == positive_label
        true_pos = true == positive_label
        if pred_pos and true_pos:
            tp += 1
        elif pred_pos and not true_pos:
            fp += 1
        elif not pred_pos and not true_pos:
            tn += 1
        else:
            fn += 1
    return ConfusionMatrix(tp=tp, fp=fp, tn=tn, fn=fn, positive_label=positive_label)


class BinaryClassificationMetric(ClassificationMetric):
    """Precision, recall, and F1 for binary classification.

    Args:
        positive_label: The label considered the positive class (default 1).
        metric: Which scalar to return from compute(): ``"f1"``, ``"precision"``,
                or ``"recall"`` (default ``"f1"``).
    """

    def __init__(
        self,
        positive_label: Any = 1,
        metric: Literal["f1", "precision", "recall"] = "f1",
    ) -> None:
        if metric not in ("f1", "precision", "recall"):
            raise ValueError(f"metric must be 'f1', 'precision', or 'recall', got {metric!r}")
        self._positive_label = positive_label
        self._metric = metric

    @property
    def name(self) -> str:
        return f"binary_{self._metric}"

    def confusion(self, prediction: list, ground_truth: list) -> ConfusionMatrix:
        """Return binary ConfusionMatrix for the given predictions."""
        return _build_binary_confusion(prediction, ground_truth, self._positive_label)

    def compute(self, prediction: list, ground_truth: list, context: Any = None) -> float:
        """Return the configured scalar metric (f1 / precision / recall).

        Args:
            prediction: Flat list of predicted labels.
            ground_truth: Flat list of true labels (same length).
            context: Unused.

        Returns:
            Float score in [0.0, 1.0].
        """
        trace_id = _trace_id(
            "BinaryClassificationMetric.compute",
            f"{len(prediction)}|{len(ground_truth)}|{self._positive_label}|{self._metric}",
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "BinaryClassificationMetric.compute",
        )

        if not prediction or not ground_truth:
            return 0.0
        cm = self.confusion(prediction, ground_truth)
        if self._metric == "precision":
            return cm.precision()
        if self._metric == "recall":
            return cm.recall()
        return cm.f1()


# ---------------------------------------------------------------------------
# MultiClassF1Metric
# ---------------------------------------------------------------------------


def _per_class_confusion(
    prediction: list,
    ground_truth: list,
    label: Any,
) -> ConfusionMatrix:
    """One-vs-rest binary confusion matrix for a single class label."""
    return _build_binary_confusion(
        prediction=[p == label for p in prediction],
        ground_truth=[g == label for g in ground_truth],
        positive_label=True,
    )


class MultiClassF1Metric(ClassificationMetric):
    """Per-class precision/recall/F1 with configurable averaging.

    Averaging modes:
        ``"macro"``    — unweighted mean of per-class F1
        ``"micro"``    — aggregate TP/FP/FN across all classes, then compute F1
        ``"weighted"`` — support-weighted mean of per-class F1

    Args:
        averaging: One of ``"macro"``, ``"micro"``, ``"weighted"`` (default ``"macro"``).
        metric: Scalar to return from compute(): ``"f1"``, ``"precision"``,
                or ``"recall"`` (default ``"f1"``).
    """

    def __init__(
        self,
        averaging: Literal["macro", "micro", "weighted"] = "macro",
        metric: Literal["f1", "precision", "recall"] = "f1",
    ) -> None:
        if averaging not in ("macro", "micro", "weighted"):
            raise ValueError(f"averaging must be 'macro', 'micro', or 'weighted', got {averaging!r}")
        if metric not in ("f1", "precision", "recall"):
            raise ValueError(f"metric must be 'f1', 'precision', or 'recall', got {metric!r}")
        self._averaging = averaging
        self._metric = metric

    @property
    def name(self) -> str:
        return f"multiclass_{self._metric}_{self._averaging}"

    def _classes(self, prediction: list, ground_truth: list) -> list:
        """Sorted unique labels from both lists."""
        return sorted(set(prediction) | set(ground_truth), key=lambda x: str(x))

    def confusion(self, prediction: list, ground_truth: list) -> ConfusionMatrix:
        """Return micro-aggregate ConfusionMatrix (sum of per-class TP/FP/TN/FN)."""
        trace_id = _trace_id(
            "MultiClassF1Metric.confusion",
            f"{len(prediction)}|{len(ground_truth)}|{self._averaging}|{self._metric}",
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "MultiClassF1Metric.confusion",
        )

        classes = self._classes(prediction, ground_truth)
        tp = fp = tn = fn = 0
        for label in classes:
            cm = _per_class_confusion(prediction, ground_truth, label)
            tp += cm.tp
            fp += cm.fp
            tn += cm.tn
            fn += cm.fn
        return ConfusionMatrix(tp=tp, fp=fp, tn=tn, fn=fn, positive_label="<micro>")

    def per_class_scores(self, prediction: list, ground_truth: list) -> dict[Any, dict[str, float]]:
        """Return per-class dict of precision/recall/f1/support."""
        classes = self._classes(prediction, ground_truth)
        result: dict[Any, dict[str, float]] = {}
        for label in classes:
            cm = _per_class_confusion(prediction, ground_truth, label)
            support = sum(1 for g in ground_truth if g == label)
            result[label] = {
                "precision": cm.precision(),
                "recall": cm.recall(),
                "f1": cm.f1(),
                "support": float(support),
            }
        return result

    def compute(self, prediction: list, ground_truth: list, context: Any = None) -> float:
        """Return averaged scalar metric.

        Args:
            prediction: Flat list of predicted class labels.
            ground_truth: Flat list of true class labels (same length).
            context: Unused.

        Returns:
            Averaged score in [0.0, 1.0].
        """
        if not prediction or not ground_truth:
            return 0.0
        if len(prediction) != len(ground_truth):
            raise ValueError(
                f"prediction length {len(prediction)} != ground_truth length {len(ground_truth)}",
            )

        classes = self._classes(prediction, ground_truth)
        n = len(ground_truth)

        if self._averaging == "micro":
            cm = self.confusion(prediction, ground_truth)
            if self._metric == "precision":
                return cm.precision()
            if self._metric == "recall":
                return cm.recall()
            return cm.f1()

        per_class = self.per_class_scores(prediction, ground_truth)

        if self._averaging == "macro":
            scores = [per_class[lbl][self._metric] for lbl in classes]
            return round(sum(scores) / len(scores), 6) if scores else 0.0

        # weighted
        total_weight = 0.0
        weighted_sum = 0.0
        for lbl in classes:
            support = per_class[lbl]["support"]
            weighted_sum += per_class[lbl][self._metric] * support
            total_weight += support
        return round(weighted_sum / total_weight, 6) if total_weight > 0 else 0.0


__all__ = [
    "ConfusionMatrix",
    "BinaryClassificationMetric",
    "MultiClassF1Metric",
]
