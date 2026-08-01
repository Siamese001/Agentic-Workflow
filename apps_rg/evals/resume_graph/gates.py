"""Named release-target and candidate-threshold gate calculations."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from apps_rg.evals.resume_graph.constants import _RELEASE_TARGETS, FAIL, PASS


def _label_summary(
    prefix: str, labels: Sequence[bool], predictions: Sequence[bool | None]
) -> dict[str, float | None]:
    if not labels:
        return {
            f"{prefix}_accuracy": None,
            f"{prefix}_prediction_accuracy": None,
            f"{prefix}_precision": None,
            f"{prefix}_recall": None,
            f"{prefix}_predicted_positive_rate": None,
            f"{prefix}_labeled_positive_rate": None,
        }
    count = len(labels)
    positive_rate = sum(labels) / count
    if len(predictions) != count or any(type(value) is not bool for value in predictions):
        return {
            f"{prefix}_accuracy": positive_rate,
            f"{prefix}_prediction_accuracy": None,
            f"{prefix}_precision": None,
            f"{prefix}_recall": None,
            f"{prefix}_predicted_positive_rate": None,
            f"{prefix}_labeled_positive_rate": positive_rate,
        }
    true_positive = sum(prediction and label for prediction, label in zip(predictions, labels))
    predicted_positive = sum(predictions)
    labeled_positive = sum(labels)
    return {
        # The release accuracy is the human-confirmed success rate.  Prediction
        # diagnostics are separate so a trivial negative classifier cannot pass.
        f"{prefix}_accuracy": positive_rate,
        f"{prefix}_prediction_accuracy": sum(
            prediction == label for prediction, label in zip(predictions, labels)
        )
        / count,
        f"{prefix}_precision": true_positive / predicted_positive if predicted_positive else None,
        f"{prefix}_recall": true_positive / labeled_positive if labeled_positive else None,
        f"{prefix}_predicted_positive_rate": predicted_positive / count,
        f"{prefix}_labeled_positive_rate": labeled_positive / count,
    }


def _select_candidate_threshold(
    probabilities: Sequence[float],
    labels: Sequence[bool],
    *,
    precision_floor: float,
    minimum_threshold: float,
    minimum_positive_count: int,
) -> dict[str, Any] | None:
    candidates = sorted(
        {float(probability) for probability in probabilities if probability >= minimum_threshold}
        | ({minimum_threshold} if minimum_threshold <= 1.0 else set())
    )
    eligible: list[dict[str, Any]] = []
    total_positive = sum(labels)
    for threshold in candidates:
        selected = [index for index, probability in enumerate(probabilities) if probability >= threshold]
        if len(selected) < minimum_positive_count:
            continue
        true_positive = sum(labels[index] for index in selected)
        precision = true_positive / len(selected)
        recall = true_positive / total_positive if total_positive else 0.0
        if precision >= precision_floor:
            eligible.append(
                {
                    "threshold": threshold,
                    "precision": precision,
                    "recall": recall,
                    "predicted_positive_count": len(selected),
                    "true_positive_count": true_positive,
                    "selection_split": "proof_split:calibration",
                }
            )
    if not eligible:
        return None
    return sorted(
        eligible,
        key=lambda item: (-item["recall"], -item["precision"], item["threshold"]),
    )[0]


def _future_release_candidate_summary(
    holdout_rows: Sequence[Mapping[str, Any]],
    probabilities: Sequence[float],
    *,
    candidate_threshold: Mapping[str, Any] | None,
) -> dict[str, Any]:
    scope = "canonical_visible_unique_proof_identities_at_or_above_candidate_threshold"
    canonical = [
        (row, float(probability))
        for row, probability in zip(holdout_rows, probabilities)
        if row.get("representation_mode", "CANONICAL_VISIBLE") == "CANONICAL_VISIBLE"
    ]
    if candidate_threshold is None:
        return {
            "scope": scope,
            "precision": None,
            "recall": None,
            "support_count": 0,
            "minimum_calibrated_confidence": None,
            "activation_status": "UNPROMOTED",
        }
    threshold = float(candidate_threshold["threshold"])
    selected = [(row, probability) for row, probability in canonical if probability >= threshold]
    support = len(selected)
    true_positive = sum(bool(row["proof_label"]) for row, _ in selected)
    total_positive = sum(bool(row["proof_label"]) for row, _ in canonical)
    return {
        "scope": scope,
        "precision": true_positive / support if support else None,
        "recall": true_positive / total_positive if total_positive else None,
        "support_count": support,
        "minimum_calibrated_confidence": (
            min(probability for _, probability in selected) if selected else None
        ),
        "activation_status": "UNPROMOTED",
    }


def _gate_results(
    metrics: Mapping[str, float | None], release_targets: Mapping[str, Any]
) -> tuple[dict[str, Any], bool]:
    results: dict[str, Any] = {}
    passed = True
    for target_name, (metric_name, direction) in _RELEASE_TARGETS.items():
        threshold = release_targets.get(target_name)
        value = metrics.get(metric_name)
        if threshold is None:
            results[target_name] = {
                "metric": metric_name,
                "direction": direction,
                "threshold": None,
                "value": value,
                "status": "NOT_GATED",
            }
            continue
        if value is None:
            target_pass = False
        elif direction == "minimum":
            target_pass = value >= float(threshold)
        else:
            target_pass = value <= float(threshold)
        passed = passed and target_pass
        results[target_name] = {
            "metric": metric_name,
            "direction": direction,
            "threshold": float(threshold),
            "value": value,
            "status": PASS if target_pass else FAIL,
        }
    return results, passed
