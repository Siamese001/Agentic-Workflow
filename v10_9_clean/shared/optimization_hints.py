# optimization_hints.py
"""
Shared Optimization Hints — v10_9
"""

from __future__ import annotations
from typing import Any, Dict, List


def compute_optimization_hint(
    spans: List[Dict[str, Any]],
    tokens: List[Dict[str, Any]] | None = None,
    retries: int = 0,
) -> Dict[str, Any]:

    tokens = tokens or []

    planning_ms = _find(spans, "planning")
    execution_ms = _find(spans, "execution")
    reviewing_ms = _find(spans, "reviewing")

    total_tokens = sum(t.get("total_tokens", 0) for t in tokens)
    completion_tokens = sum(t.get("completion_tokens", 0) for t in tokens)

    score = 0.0
    reasons = []

    if planning_ms > execution_ms * 2:
        score += 1.5
        reasons.append("Planning dominates execution time.")

    if reviewing_ms > execution_ms * 1.5:
        score += 1.2
        reasons.append("Reviewing time too high.")

    if total_tokens > 4000:
        score += 1.0
        reasons.append("High total token usage.")

    if retries > 0:
        score += retries * 0.5
        reasons.append(f"{retries} retries detected.")

    if score >= 3.0:
        suggestion = "optimize_aggressively"
    elif score >= 1.5:
        suggestion = "optimize"
    else:
        suggestion = "normal"

    return {
        "suggestion": suggestion,
        "score": score,
        "reasons": reasons,
        "metrics": {
            "planning_ms": planning_ms,
            "execution_ms": execution_ms,
            "reviewing_ms": reviewing_ms,
            "total_tokens": total_tokens,
            "completion_tokens": completion_tokens,
            "retries": retries,
        },
    }


def _find(spans: List[Dict[str, Any]], name: str) -> float:
    for s in spans:
        if s.get("name") == name:
            return float(s.get("duration_ms", 0))
    return 0.0
