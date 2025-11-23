from __future__ import annotations

from typing import Dict, Iterable

from eval.golden_state.models import JudgeVerdict


def aggregate_scores(verdicts: Iterable[JudgeVerdict]) -> Dict[str, float]:
    """Aggregate judge verdicts into simple metrics.

    Returns a dict with:
        - avg_score
        - pass_count
        - fail_count
        - total
    """

    vs = list(verdicts)
    total = len(vs)
    if not total:
        return {"avg_score": 0.0, "pass_count": 0.0, "fail_count": 0.0, "total": 0.0}

    total_score = sum(v.score for v in vs)
    pass_count = sum(1 for v in vs if v.rating == "pass")
    fail_count = sum(1 for v in vs if v.rating == "fail")

    return {
        "avg_score": total_score / total,
        "pass_count": float(pass_count),
        "fail_count": float(fail_count),
        "total": float(total),
    }
