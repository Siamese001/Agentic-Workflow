"""Offline proof-score calibration metrics."""

from __future__ import annotations

from typing import Any, Sequence

from apps_rg.evals.resume_graph.metrics.retrieval import _mean
from apps_rg.evals.resume_graph.models import (
    EvaluationDataError,
    IsotonicModel,
    _is_number,
)


def expected_calibration_error(
    probabilities: Sequence[float], labels: Sequence[bool], *, n_bins: int = 10
) -> float:
    """Calculate equal-width binary expected calibration error."""

    _validate_binary_inputs(probabilities, labels)
    if n_bins <= 0:
        raise EvaluationDataError("n_bins must be positive")
    count = len(probabilities)
    error = 0.0
    for bin_index in range(n_bins):
        lower = bin_index / n_bins
        upper = (bin_index + 1) / n_bins
        indices = [
            index
            for index, probability in enumerate(probabilities)
            if probability >= lower
            and (probability < upper or (bin_index == n_bins - 1 and probability <= 1.0))
        ]
        if not indices:
            continue
        confidence = _mean([float(probabilities[index]) for index in indices])
        accuracy = _mean([float(labels[index]) for index in indices])
        error += (len(indices) / count) * abs(accuracy - confidence)
    return error


def brier_score(probabilities: Sequence[float], labels: Sequence[bool]) -> float:
    """Calculate mean squared probability error for binary proof labels."""

    _validate_binary_inputs(probabilities, labels)
    return _mean(
        [(float(probability) - float(label)) ** 2 for probability, label in zip(probabilities, labels)]
    )


def _validate_binary_inputs(probabilities: Sequence[float], labels: Sequence[bool]) -> None:
    if not probabilities or len(probabilities) != len(labels):
        raise EvaluationDataError("probabilities and labels must be nonempty and equally sized")
    if any(
        not _is_number(probability) or not 0.0 <= float(probability) <= 1.0 for probability in probabilities
    ):
        raise EvaluationDataError("probabilities must be finite values in [0, 1]")
    if any(type(label) is not bool for label in labels):
        raise EvaluationDataError("labels must be booleans")


def _validate_fit_inputs(scores: Sequence[float], labels: Sequence[bool]) -> None:
    if not scores or len(scores) != len(labels):
        raise EvaluationDataError("proof scores and labels must be nonempty and equally sized")
    if any(not _is_number(score) for score in scores):
        raise EvaluationDataError("raw proof scores must be finite numeric values")
    if any(type(label) is not bool for label in labels):
        raise EvaluationDataError("labels must be booleans")


def fit_isotonic_pav(scores: Sequence[float], labels: Sequence[bool]) -> IsotonicModel:
    """Fit deterministic binary isotonic regression with pool-adjacent violators."""

    _validate_fit_inputs(scores, labels)
    if len(set(labels)) < 2:
        raise EvaluationDataError("isotonic calibration requires both proof-label classes")

    grouped: dict[float, list[bool]] = {}
    for score, label in zip(scores, labels):
        grouped.setdefault(float(score), []).append(label)
    if len(grouped) < 2:
        raise EvaluationDataError("isotonic calibration requires two distinct proof scores")

    blocks: list[dict[str, Any]] = []
    for score in sorted(grouped):
        group_labels = grouped[score]
        blocks.append(
            {
                "scores": [score],
                "weight": len(group_labels),
                "positive": sum(group_labels),
            }
        )
        while len(blocks) >= 2:
            left = blocks[-2]
            right = blocks[-1]
            left_mean = left["positive"] / left["weight"]
            right_mean = right["positive"] / right["weight"]
            if left_mean <= right_mean:
                break
            blocks[-2:] = [
                {
                    "scores": left["scores"] + right["scores"],
                    "weight": left["weight"] + right["weight"],
                    "positive": left["positive"] + right["positive"],
                }
            ]

    fitted: dict[float, float] = {}
    for block in blocks:
        probability = block["positive"] / block["weight"]
        for score in block["scores"]:
            fitted[score] = probability
    x_values = tuple(sorted(fitted))
    return IsotonicModel(x_values=x_values, y_values=tuple(fitted[x] for x in x_values))
