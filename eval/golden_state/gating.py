from __future__ import annotations

from typing import Dict


def gate_experiment(new_scores: Dict[str, float], baseline_scores: Dict[str, float]) -> bool:
    """Return True if the experiment meets or exceeds baseline.

    For now we only enforce that avg_score is not worse and that
    pass_count is not lower when both metrics are present.
    """

    if not baseline_scores:
        # No baseline recorded yet → allow by default.
        return True

    new_avg = float(new_scores.get("avg_score", 0.0))
    base_avg = float(baseline_scores.get("avg_score", 0.0))

    if new_avg < base_avg:
        return False

    if "pass_count" in baseline_scores and "pass_count" in new_scores:
        if float(new_scores["pass_count"]) < float(baseline_scores["pass_count"]):
            return False

    return True


def gate_against_baseline(
    current_scores: Dict[str, float],
    baseline_scores: Dict[str, float],
    tolerance: float = 0.0,
) -> bool:
    if not baseline_scores:
        return True

    adjusted_baseline = dict(baseline_scores)
    base_avg = float(baseline_scores.get("avg_score", 0.0))
    adjusted_baseline["avg_score"] = max(0.0, base_avg - tolerance)
    return gate_experiment(current_scores, adjusted_baseline)
