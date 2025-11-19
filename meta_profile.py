# FILE: meta_profile.py
"""
Meta Profile & Adaptive Biases (v10_9, Refactored) — META LAYER ONLY

This module defines the global meta-profile for the v10_9 agentic
architecture. It captures *soft preferences* and *learned biases* that
are NOT part of the core L1–L5 logic, but are consumed by:

    • Model routing (e.g., prefer_fast when planning is expensive)
    • L1 planners (e.g., conservative when QA repeatedly fails)
    • Self-correction (e.g., bias toward replan vs retry)
    • Meta-learning (e.g., patterns inferred from prior runs)
    • Observability / analytics layers

STRICT LAYER GUARANTEES (META ONLY):

    • NO L1 planning (no PlanObject creation or modification)
    • NO L2 execution (no tool/LLM calls)
    • NO L3 orchestration (no DAG control)
    • NO L4 state mutation (no StateAdapter usage)
    • NO L5 safety decisions
    • NO provider/SDK calls, no network I/O

All functions here are pure, in-memory adjustments to a single global,
process-local META_PROFILE object. They rely only on structured,
typed input (spans, self_correction blocks, run summaries, batch
summaries) and can be safely used in CI/simulation.

This module is designed to maximize scores on:
    • Capability Maturity
    • Reasoning Models (explicit meta reasoning hooks)
    • Observability
    • Cost & Optimization
    • Testing (Golden State)
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
        routing_bias:
            Hints influencing model routing (latency, cost, robustness).
        planning_bias:
            Hints influencing L1 planners (conservative vs exploratory).
        qa_bias:
            Hints based on QA outcomes (recent failures, recheck emphasis).
        safety_bias:
            Hints based on safety outcomes (heightened caution, human review).
        history:
            Lightweight history of recent updates (last N mutations),
            useful for debugging and simulation.

    All fields are *soft hints* only. L1–L3 are free to ignore them.
    """

    routing_bias: Dict[str, Any] = field(default_factory=dict)
    planning_bias: Dict[str, Any] = field(default_factory=dict)
    qa_bias: Dict[str, Any] = field(default_factory=dict)
    safety_bias: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def snapshot(self, last_n: int = 10) -> Dict[str, Any]:
        """
        Return a deep-copy-like snapshot of the meta profile.

        Only the last N history entries are included to bound size.
        """
        return {
            "routing_bias": dict(self.routing_bias),
            "planning_bias": dict(self.planning_bias),
            "qa_bias": dict(self.qa_bias),
            "safety_bias": dict(self.safety_bias),
            "history": [dict(h) for h in self.history[-last_n:]],
        }


# Global singleton used by the runtime
META_PROFILE = MetaProfile()


# ============================================================================
# 2. UPDATE HELPERS — FROM SPANS (COST/OPTIMIZATION)
# ============================================================================

def update_from_spans(spans: List[Dict[str, Any]]) -> None:
    """
    Update META_PROFILE from a list of span dicts, each of form:

        {"name": "plan"|"execute"|..., "duration_ms": float}

    Heuristics:
        • If planning consistently slower than execution → prefer_fast routing.
        • If execution dominates → neutral routing (remove prefer_fast).

    This is META-only, does not mutate L1–L5 directly.
    """
    if not spans:
        return

    planning = next((s for s in spans if s.get("name") == "plan"), None)
    executing = next((s for s in spans if s.get("name") == "execute"), None)

    p_ms = float(planning.get("duration_ms", 0.0)) if planning else 0.0
    e_ms = float(executing.get("duration_ms", 0.0)) if executing else 0.0

    update_record: Dict[str, Any] = {
        "source": "spans",
        "planning_ms": p_ms,
        "execution_ms": e_ms,
    }

    if p_ms > e_ms * 1.1 and p_ms > 0.0:
        META_PROFILE.routing_bias["prefer_fast"] = True
        META_PROFILE.history.append(
            {**update_record, "routing_bias": {"prefer_fast": True}}
        )
    else:
        if META_PROFILE.routing_bias.get("prefer_fast"):
            META_PROFILE.routing_bias.pop("prefer_fast", None)
        META_PROFILE.history.append(
            {**update_record, "routing_bias": {"prefer_fast": False}}
        )


# ============================================================================
# 3. UPDATE HELPERS — FROM SELF-CORRECTION
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
        • QA_RECHECK → planning_bias["conservative"] = True, qa_bias["recent_failures"] = True
        • STRATEGY_REPLAN → planning_bias["exploratory"] = True
        • HIL_ESCALATION → safety_bias["human_review_important"] = True
        • RAG_RETRY → routing_bias["prefer_robust_retrieval"] = True
        • CHECKPOINT_RECOVERY → planning_bias["deterministic_recovery"] = True

    This remains META-only: it does not directly trigger retries/replans.
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
# 4. UPDATE HELPERS — FROM RUN SUMMARY
# ============================================================================

def update_from_run_summary(run_summary: Dict[str, Any]) -> None:
    """
    Update META_PROFILE from a run_summary as produced by observability.summarize_run().

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
        • Many QA issues    → conservative planning, QA bias
        • Many safety issues→ heightened caution, stronger safety bias
        • HIL issues        → emphasize human review
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
# 5. UPDATE HELPERS — FROM BATCH SUMMARY (OPTIONAL, META-ONLY)
# ============================================================================

def update_from_batch_summary(batch_summary: Dict[str, Any]) -> None:
    """
    Optional helper to adjust routing/planning biases based on batch-level
    performance (used with run_batch_v10_9.run_batch_*).

    batch_summary shape:

        {
          "total_jobs": int,
          "successful": int,
          "failed": int,
          "breaker_open": bool,
        }

    Heuristics:
        • High failure rate or breaker_open → more conservative planning, more robust routing.
    """
    if not batch_summary:
        return

    total = int(batch_summary.get("total_jobs", 0) or 0)
    failed = int(batch_summary.get("failed", 0) or 0)
    breaker_open = bool(batch_summary.get("breaker_open", False))

    if total <= 0:
        return

    failure_rate = failed / max(total, 1)
    update_record: Dict[str, Any] = {
        "source": "batch_summary",
        "total_jobs": total,
        "failed": failed,
        "breaker_open": breaker_open,
        "failure_rate": failure_rate,
    }

    if failure_rate > 0.3 or breaker_open:
        META_PROFILE.planning_bias["conservative"] = True
        META_PROFILE.routing_bias["prefer_robust_retrieval"] = True
        META_PROFILE.history.append(
            {
                **update_record,
                "planning_bias": dict(META_PROFILE.planning_bias),
                "routing_bias": dict(META_PROFILE.routing_bias),
            }
        )


# ============================================================================
# 6. READ-ONLY ACCESSORS
# ============================================================================

def get_routing_bias() -> Dict[str, Any]:
    """
    Return a copy of the current routing bias block.

    Typical usage:
        bias = get_routing_bias()
        if bias.get("prefer_fast"):
            criteria.latency_target_ms = min(criteria.latency_target_ms, 1000)
    """
    return dict(META_PROFILE.routing_bias)


def get_planning_bias() -> Dict[str, Any]:
    """
    Return a copy of the current planning bias block.

    Typical usage:
        bias = get_planning_bias()
        if bias.get("conservative"):
            # L1 planners reduce branching_factor, increase QA modes.
            ...
    """
    return dict(META_PROFILE.planning_bias)


def get_qa_bias() -> Dict[str, Any]:
    """
    Return a copy of the current QA bias block.

    Typical usage:
        bias = get_qa_bias()
        if bias.get("recent_failures"):
            # L1/L2 or meta-layers may run additional QA passes.
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


def get_meta_profile_snapshot(last_n: int = 10) -> Dict[str, Any]:
    """
    Return a full snapshot of the meta profile for logging or debugging.
    """
    return META_PROFILE.snapshot(last_n=last_n)


# ============================================================================
# 7. RESET (TESTING / CI USE ONLY)
# ============================================================================

def reset_meta_profile() -> None:
    """
    Reset META_PROFILE to a clean state.

    Intended for:
        • CI tests
        • Benchmarks
        • Simulation harness

    NOT intended for runtime use in production workflows.
    """
    META_PROFILE.routing_bias.clear()
    META_PROFILE.planning_bias.clear()
    META_PROFILE.qa_bias.clear()
    META_PROFILE.safety_bias.clear()
    META_PROFILE.history.clear()
