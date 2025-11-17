"""
Optimization hint computation for v10_9 runtime.

This component provides deterministic, side-effect-free optimization
signals based on:
  • span durations from CostTracker
  • token usage patterns
  • retry counts
  • imbalance across phases (planning vs execution vs reviewing)

Hints are consumed by L3 orchestration to adjust:
  • routing
  • retry strategy
  • model selection
  • batching and tool sequence decisions
"""

from __future__ import annotations

from typing import Any, Dict, List


# ======================================================================
# INTERNAL HELPERS
# ======================================================================

def _get_span(spans: List[Dict[str, Any]], name: str) -> float:
    """Return duration in ms for a named span."""
    s = next((x for x in spans if x.get("name") == name), None)
    if not s:
        return 0.0
    return float(s.get("duration_ms", 0.0))


def _ratio(a: float, b: float) -> float:
    """Safe ratio helper."""
    if b <= 0:
        return 0.0
    return a / b


# ======================================================================
# MAIN API
# ======================================================================

def compute_optimization_hint(
    spans: List[Dict[str, Any]],
    tokens: List[Dict[str, Any]] | None = None,
    retries: int = 0,
) -> Dict[str, Any]:
    """
    Deterministic optimization hint engine.

    Produces:
      • suggestion:   high-level guidance class
      • score:        numeric optimization signal
      • reasons:      human-readable explanations

    Hints influence L3 orchestration but do not mutate state.
    """

    tokens = tokens or []

    # ------------------------------------------------------------------
    # Extract durations
    # ------------------------------------------------------------------
    planning_ms = _get_span(spans, "planning")
    execution_ms = _get_span(spans, "execution")
    reviewing_ms = _get_span(spans, "reviewing")

    # ------------------------------------------------------------------
    # Token aggregates
    # ------------------------------------------------------------------
    total_tokens = sum(t.get("total_tokens", 0) for t in tokens)
    completion_tokens = sum(t.get("completion_tokens", 0) for t in tokens)

    # ------------------------------------------------------------------
    # Simple scoring model
    # ------------------------------------------------------------------
    score = 0.0
    reasons = []

    # Imbalance: planning dominating execution → too much cognition
    plan_exec_ratio = _ratio(planning_ms, execution_ms)
    if plan_exec_ratio > 2.0:
        score += 1.5
        reasons.append("Planning is disproportionately long relative to execution.")

    # Excessive reviewing overhead
    exec_review_ratio = _ratio(reviewing_ms, execution_ms)
    if exec_review_ratio > 1.5:
        score += 1.2
        reasons.append("Reviewing time is significantly higher than execution.")

    # Token usage signals
    if total_tokens > 4000:
        score += 1.0
        reasons.append("High overall token usage.")
    if completion_tokens > 2000:
        score += 0.8
        reasons.append("High completion token usage.")

    # Retry penalty
    if retries > 0:
        score += retries * 0.5
        reasons.append(f"{retries} retries detected.")

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
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
