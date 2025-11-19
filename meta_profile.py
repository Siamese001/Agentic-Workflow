# FILE: meta_profile.py
"""
Meta Profile & Adaptive Biases (v10_9) — META LAYER ONLY

This module defines the global meta-profile for the v10_9 agentic
architecture. It captures *soft preferences* and *learned biases* that
are NOT part of the core L1–L5 logic, but are used by:

    • Model routing (e.g., "prefer_fast" when planning dominates cost).
    • L1 planners (e.g., "conservative" when QA repeatedly fails).
    • Self-correction (e.g., bias toward replan vs retry).
    • Meta-learning (e.g., patterns inferred from prior runs).

Layer constraints (Agentic Guardrails):

    • NO L1 planning (no PlanObject creation).
    • NO L2 execution (no tool/LLM calls).
    • NO L3 DAG/orchestration.
    • NO L4 state mutation (no StateAdapter usage).
    • NO L5 safety decisions.

This module is a META layer “tuning brain” that keeps track of heuristics
such as "we're too slow, route fast" or "QA failures are frequent, plan
more conservatively" without violating layer purity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================================
# 1. META PROFILE DATA CLASS
# ============================================================================


@dataclass
class MetaProfile:
    """
    Global meta-configuration for adaptive behavior.

    Fields:
        • routing_bias:    knobs influencing model routing.
        • planning_bias:   knobs influencing L1 planners.
        • qa_bias:         knobs based on QA outcomes.
        • safety_bias:     knobs based on safety outcomes.
        • history:         recent meta-updates (for inspection and tests).

    All fields are *soft hints* only. L1–L3 are free to ignore them.
    This object is pure data; update_* helpers below mutate it.
    """

    routing_bias: Dict[str, Any] = field(default_factory=dict)
    planning_bias: Dict[str, Any] = field(default_factory=dict)
    qa_bias: Dict[str, Any] = field(default_factory=dict)
    safety_bias: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a deep copy-like snapshot safe for logging or inspection.
        Only the last N history entries are preserved to bound size.
        """
        return {
            "routing_bias": dict(self.routing_bias),
            "planning_bias": dict(self.planning_bias),
            "qa_bias": dict(self.qa_bias),
            "safety_bias": dict(self.safety_bias),
            "history": [dict(h) for h in self.history[-10:]],  # last 10 updates
        }


# Global singleton used by the runtime
META_PROFILE = MetaProfile()


# ============================================================================
# 2. UPDATE HELPERS (SPAN-BASED)
# ============================================================================


def update_from_spans(spans: List[Dict[str, Any]]) -> None:
    """
    Update META_PROFILE from a list of span dicts, each of form:

        {"name": "planning"|"execution"|..., "duration_ms": float}

    Heuristics:
        • If planning consistently slower than execution → prefer_fast routing.
        • If execution is consistently dominant → neutral routing.

    This is a META-only adjustment; it does not mutate L1–L5 directly.
    """
    if not spans:
        return

    # Extract planning/execution durations
    planning = next((s for s in spans if s.get("name") == "planning"), None)
    execution = next((s for s in spans if s.get("name") == "execution"), None)

    p_ms = float(planning.get("duration_ms", 0.0)) if planning else 0.0
    e_ms = float(execution.get("duration_ms", 0.0)) if execution else 0.0

    update_record: Dict[str, Any] = {
        "source": "spans",
        "planning_ms": p_ms,
        "execution_ms": e_ms,
    }

    # If planning is significantly more expensive, we bias toward "fast" models.
    if p_ms > e_ms * 1.1 and p_ms > 0.0:
        META_PROFILE.routing_bias["prefer_fast"] = True
        META_PROFILE.history.append(
            {**update_record, "routing_bias": {"prefer_fast": True}}
        )
    else:
        # Remove the bias if it is no longer justified.
        if META_PROFILE.routing_bias.get("prefer_fast"):
            META_PROFILE.routing_bias.pop("prefer_fast", None)
        META_PROFILE.history.append(
            {**update_record, "routing_bias": {"prefer_fast": False}}
        )


# ============================================================================
# 3. UPDATE HELPERS (SELF-CORRECTION-BASED)
# ============================================================================


def update_from_self_correction(self_correction_block: Dict[str, Any]) -> None:
    """
    Update META_PROFILE from a self_correction block, typically derived
    from self_correction.CorrectionRecommendation.to_dict().

    Example block:

        {
          "needed": True,
          "surface": "qa_recheck",
          "rationale": "...",
          "metadata": {...}
        }

    Heuristics:
        • QA_RECHECK frequently → planning_bias["conservative"] = True.
        • STRATEGY_REPLAN frequently → planning_bias["exploratory"] = True.
        • HIL_ESCALATION frequently → safety_bias["human_review_important"] = True.
        • RAG_RETRY frequently → routing_bias["prefer_robust_retrieval"] = True.
        • CHECKPOINT_RECOVERY → planning_bias["deterministic_recovery"] = True.
    """
    if not self_correction_block:
        return

    needed = bool(self_correction_block.get("needed", False))
    surface = str(self_correction_block.get("surface") or "")

    if not needed or not surface:
        return

    update_record = {
        "source": "self_correction",
        "surface": surface,
        "rationale": self_correction_block.get("rationale", ""),
    }

    # Simple surface-based adjustment
    if surface == "qa_recheck":
        META_PROFILE.planning_bias["conservative"] = True
        META_PROFILE.qa_bias["recent_failures"] = True
        META_PROFILE.history.append(
            {**update_record, "planning_bias": {"conservative": True}}
        )
    elif surface == "strategy_replan":
        META_PROFILE.planning_bias["exploratory"] = True
        META_PROFILE.history.append(
            {**update_record, "planning_bias": {"exploratory": True}}
        )
    elif surface == "hil_escalation":
        META_PROFILE.safety_bias["human_review_important"] = True
        META_PROFILE.history.append(
            {**update_record, "safety_bias": {"human_review_important": True}}
        )
    elif surface == "rag_retry":
        META_PROFILE.routing_bias["prefer_robust_retrieval"] = True
        META_PROFILE.history.append(
            {**update_record, "routing_bias": {"prefer_robust_retrieval": True}}
        )
    elif surface == "checkpoint_recovery":
        META_PROFILE.planning_bias["deterministic_recovery"] = True
        META_PROFILE.history.append(
            {**update_record, "planning_bias": {"deterministic_recovery": True}}
        )


# ============================================================================
# 4. UPDATE HELPERS (RUN SUMMARY-BASED)
# ============================================================================


def update_from_run_summary(run_summary: Dict[str, Any]) -> None:
    """
    Optional hook: update META_PROFILE from a run_summary as produced
    by observability.summarize_run().

    Shape:

        {
          "workflow_id": str,
          "phases": [...],
          "timings": {...},
          "counts": {...},
          "issues": {
            "qa": [...],
            "safety": [...],
            "hil": [...],
            ...
          },
        }

    Heuristics:
        • Many QA issues → conservative planning.
        • Many safety issues → stronger safety biases.
        • HIL issues → more emphasis on human review.
    """
    if not run_summary:
        return

    issues = run_summary.get("issues") or {}
    qa_issues = issues.get("qa") or []
    safety_issues = issues.get("safety") or []
    hil_issues = issues.get("hil") or []

    update_record: Dict[str, Any] = {
        "source": "run_summary",
        "qa_issue_count": len(qa_issues),
        "safety_issue_count": len(safety_issues),
        "hil_issue_count": len(hil_issues),
    }

    if qa_issues:
        META_PROFILE.planning_bias["conservative"] = True
        META_PROFILE.qa_bias["recent_failures"] = True

    if safety_issues:
        META_PROFILE.safety_bias["heightened_caution"] = True

    if hil_issues:
        META_PROFILE.safety_bias["human_review_important"] = True

    META_PROFILE.history.append(
        {
            **update_record,
            "planning_bias": dict(META_PROFILE.planning_bias),
            "safety_bias": dict(META_PROFILE.safety_bias),
        }
    )


# ============================================================================
# 5. READ-ONLY ACCESSORS
# ============================================================================


def get_routing_bias() -> Dict[str, Any]:
    """
    Return a copy of the current routing bias block.

    Typical usage:
        criteria = RoutingCriteria(...)
        if get_routing_bias().get("prefer_fast"):
            criteria.latency_target_ms = min(criteria.latency_target_ms, 1000)
    """
    return dict(META_PROFILE.routing_bias)


def get_planning_bias() -> Dict[str, Any]:
    """
    Return a copy of the current planning bias block.

    Typical usage:
        bias = get_planning_bias()
        if bias.get("conservative"):
            # L1 planners may reduce branching_factor.
            ...
    """
    return dict(META_PROFILE.planning_bias)


def get_qa_bias() -> Dict[str, Any]:
    """
    Return a copy of the current QA bias block.

    Typical usage:
        bias = get_qa_bias()
        if bias.get("recent_failures"):
            # L1/L2 or meta layers may run additional QA passes.
            ...
    """
    return dict(META_PROFILE.qa_bias)


def get_safety_bias() -> Dict[str, Any]:
    """
    Return a copy of the current safety bias block.

    Typical usage:
        bias = get_safety_bias()
        if bias.get("heightened_caution"):
            # L5 or routing may use stricter models or thresholds.
            ...
    """
    return dict(META_PROFILE.safety_bias)


def get_meta_profile_snapshot() -> Dict[str, Any]:
    """
    Return a full snapshot of the meta profile for logging or debugging.
    """
    return META_PROFILE.snapshot()
