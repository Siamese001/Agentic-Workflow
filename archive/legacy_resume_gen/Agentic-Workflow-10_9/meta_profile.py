# FILE: meta_profile.py
"""
Meta Profile & Adaptive Biases (v10_9) — META LAYER ONLY (REFINED)

This module defines the global meta-profile for the v10_9 agentic
architecture. It captures *soft preferences* and *learned biases* that
are NOT part of the core L1–L5 logic, but are used by:

    • Model routing (e.g., "prefer_fast" when planning dominates cost).
    • L1 planners (e.g., "conservative" when QA repeatedly fails).
    • Self-correction (e.g., bias toward replan vs retry vs escalate).
    • Meta-learning (e.g., patterns inferred from prior runs).
    • Observability (e.g., "enable more spans when failures accumulate").

Layer constraints (Agentic Guardrails):

    • NO L1 planning (no PlanObject creation).
    • NO L2 execution (no tool/LLM calls).
    • NO L3 DAG/orchestration.
    • NO L4 state mutation (no StateAdapter usage).
    • NO L5 safety decisions.

This module is a META layer “tuning brain” that keeps track of
heuristics such as:

    • "we're too slow, route fast"
    • "QA failures are frequent, plan more conservatively"
    • "safety blocks often, escalate sooner"

without violating layer purity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


# ============================================================================
# 1. META PROFILE DATA CLASSES (TYPED BIASES)
# ============================================================================


@dataclass
class RoutingBias:
    """
    Routing-level preferences for L2/L5.

    Fields:
        prefer_fast:             prefer cheaper/faster models
        prefer_robust_retrieval: bias toward more robust RAG settings
        prefer_long_context:     bias toward long-context models
    """
    prefer_fast: bool = False
    prefer_robust_retrieval: bool = False
    prefer_long_context: bool = False


@dataclass
class PlanningBias:
    """
    Planning (L1 reasoning) preferences.

    Fields:
        conservative:           reduce branching / depth
        exploratory:            allow more branches / alternatives
        deterministic_recovery: bias toward structured recovery plans
    """
    conservative: bool = False
    exploratory: bool = False
    deterministic_recovery: bool = False


@dataclass
class QaBias:
    """
    QA-related preferences and signals.

    Fields:
        recent_failures:    QA has recently failed often
        require_extra_pass: bias toward extra QA passes
    """
    recent_failures: bool = False
    require_extra_pass: bool = False


@dataclass
class SafetyBias:
    """
    Safety-related preferences.

    Fields:
        heightened_caution:     bias toward stricter safety paths
        human_review_important: HIL review is frequently beneficial
    """
    heightened_caution: bool = False
    human_review_important: bool = False


@dataclass
class MetaUpdate:
    """
    Single meta-update record used in history.

    Fields:
        source:    "spans" | "self_correction" | "run_summary" | ...
        payload:   arbitrary context information
        deltas:    snapshot of bias fields that changed
    """
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    deltas: Dict[str, Any] = field(default_factory=dict)


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

    All fields are *soft hints* only. L1–L3–L5 are free to ignore them.
    This object is pure data; update_* helpers below mutate it.
    """

    routing_bias: RoutingBias = field(default_factory=RoutingBias)
    planning_bias: PlanningBias = field(default_factory=PlanningBias)
    qa_bias: QaBias = field(default_factory=QaBias)
    safety_bias: SafetyBias = field(default_factory=SafetyBias)
    history: List[MetaUpdate] = field(default_factory=list)

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a snapshot safe for logging or inspection.
        Only the last N history entries are preserved to bound size.
        """
        return {
            "routing_bias": dict(self.routing_bias.__dict__),
            "planning_bias": dict(self.planning_bias.__dict__),
            "qa_bias": dict(self.qa_bias.__dict__),
            "safety_bias": dict(self.safety_bias.__dict__),
            "history": [
                {
                    "source": h.source,
                    "payload": dict(h.payload),
                    "deltas": dict(h.deltas),
                }
                for h in self.history[-10:]
            ],
        }

    def _record_update(self, source: str, payload: Dict[str, Any], deltas: Dict[str, Any]) -> None:
        """
        Internal helper to append a MetaUpdate to history.
        """
        self.history.append(
            MetaUpdate(
                source=source,
                payload=dict(payload),
                deltas=dict(deltas),
            )
        )


# Global singleton used by the runtime
META_PROFILE = MetaProfile()


# ============================================================================
# 2. UPDATE HELPERS (SPAN-BASED)
# ============================================================================


def update_from_spans(spans: List[Dict[str, Any]]) -> None:
    """
    Update META_PROFILE from a list of span dicts, each of form:

        {"name": "planning"|"execution"|..., "duration_ms": float}

    Heuristics (restored from v10_8 behavior):

        • If planning consistently slower than execution → routing_bias.prefer_fast = True.
        • Else → routing_bias.prefer_fast = False.

    This is a META-only adjustment; it does not mutate L1–L5 directly.
    """
    if not spans:
        return

    planning = next((s for s in spans if s.get("name") == "planning"), None)
    execution = next((s for s in spans if s.get("name") == "execution"), None)

    p_ms = float(planning.get("duration_ms", 0.0)) if planning else 0.0
    e_ms = float(execution.get("duration_ms", 0.0)) if execution else 0.0

    payload: Dict[str, Any] = {
        "planning_ms": p_ms,
        "execution_ms": e_ms,
    }

    prefer_fast_before = META_PROFILE.routing_bias.prefer_fast

    if p_ms > e_ms * 1.1 and p_ms > 0.0:
        META_PROFILE.routing_bias.prefer_fast = True
    else:
        META_PROFILE.routing_bias.prefer_fast = False

    deltas: Dict[str, Any] = {}
    if META_PROFILE.routing_bias.prefer_fast != prefer_fast_before:
        deltas["routing_bias.prefer_fast"] = META_PROFILE.routing_bias.prefer_fast

    if deltas:
        META_PROFILE._record_update(source="spans", payload=payload, deltas=deltas)


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

    Heuristics (restored v10_8 semantics, but typed):

        • surface == "qa_recheck":
            planning_bias.conservative = True
            qa_bias.recent_failures = True

        • surface == "strategy_replan":
            planning_bias.exploratory = True

        • surface == "hil_escalation":
            safety_bias.human_review_important = True

        • surface == "rag_retry":
            routing_bias.prefer_robust_retrieval = True

        • surface == "checkpoint_recovery":
            planning_bias.deterministic_recovery = True
    """
    if not self_correction_block:
        return

    needed = bool(self_correction_block.get("needed", False))
    surface = str(self_correction_block.get("surface") or "")

    if not needed or not surface:
        return

    payload = {
        "surface": surface,
        "rationale": self_correction_block.get("rationale", ""),
        "metadata": self_correction_block.get("metadata", {}),
    }

    deltas: Dict[str, Any] = {}

    if surface == "qa_recheck":
        if not META_PROFILE.planning_bias.conservative:
            META_PROFILE.planning_bias.conservative = True
            deltas["planning_bias.conservative"] = True
        if not META_PROFILE.qa_bias.recent_failures:
            META_PROFILE.qa_bias.recent_failures = True
            deltas["qa_bias.recent_failures"] = True

    elif surface == "strategy_replan":
        if not META_PROFILE.planning_bias.exploratory:
            META_PROFILE.planning_bias.exploratory = True
            deltas["planning_bias.exploratory"] = True

    elif surface == "hil_escalation":
        if not META_PROFILE.safety_bias.human_review_important:
            META_PROFILE.safety_bias.human_review_important = True
            deltas["safety_bias.human_review_important"] = True

    elif surface == "rag_retry":
        if not META_PROFILE.routing_bias.prefer_robust_retrieval:
            META_PROFILE.routing_bias.prefer_robust_retrieval = True
            deltas["routing_bias.prefer_robust_retrieval"] = True

    elif surface == "checkpoint_recovery":
        if not META_PROFILE.planning_bias.deterministic_recovery:
            META_PROFILE.planning_bias.deterministic_recovery = True
            deltas["planning_bias.deterministic_recovery"] = True

    if deltas:
        META_PROFILE._record_update(source="self_correction", payload=payload, deltas=deltas)


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

    Heuristics (restored from v10_8 + extended):

        • Many QA issues → conservative planning, qa.recent_failures = True.
        • Many safety issues → safety_bias.heightened_caution = True.
        • Many HIL issues → safety_bias.human_review_important = True.
    """
    if not run_summary:
        return

    issues = run_summary.get("issues") or {}
    qa_issues = issues.get("qa") or []
    safety_issues = issues.get("safety") or []
    hil_issues = issues.get("hil") or []

    payload: Dict[str, Any] = {
        "qa_issue_count": len(qa_issues),
        "safety_issue_count": len(safety_issues),
        "hil_issue_count": len(hil_issues),
    }

    deltas: Dict[str, Any] = {}

    if qa_issues:
        if not META_PROFILE.planning_bias.conservative:
            META_PROFILE.planning_bias.conservative = True
            deltas["planning_bias.conservative"] = True
        if not META_PROFILE.qa_bias.recent_failures:
            META_PROFILE.qa_bias.recent_failures = True
            deltas["qa_bias.recent_failures"] = True

    if safety_issues:
        if not META_PROFILE.safety_bias.heightened_caution:
            META_PROFILE.safety_bias.heightened_caution = True
            deltas["safety_bias.heightened_caution"] = True

    if hil_issues:
        if not META_PROFILE.safety_bias.human_review_important:
            META_PROFILE.safety_bias.human_review_important = True
            deltas["safety_bias.human_review_important"] = True

    if deltas:
        META_PROFILE._record_update(source="run_summary", payload=payload, deltas=deltas)


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
    return dict(META_PROFILE.routing_bias.__dict__)


def get_planning_bias() -> Dict[str, Any]:
    """
    Return a copy of the current planning bias block.

    Typical usage:
        bias = get_planning_bias()
        if bias.get("conservative"):
            # L1 planners may reduce branching_factor.
            ...
    """
    return dict(META_PROFILE.planning_bias.__dict__)


def get_qa_bias() -> Dict[str, Any]:
    """
    Return a copy of the current QA bias block.

    Typical usage:
        bias = get_qa_bias()
        if bias.get("recent_failures"):
            # L1/L2 or meta layers may run additional QA passes.
            ...
    """
    return dict(META_PROFILE.qa_bias.__dict__)


def get_safety_bias() -> Dict[str, Any]:
    """
    Return a copy of the current safety bias block.

    Typical usage:
        bias = get_safety_bias()
        if bias.get("heightened_caution"):
            # L5 or routing may use stricter models or thresholds.
            ...
    """
    return dict(META_PROFILE.safety_bias.__dict__)


def get_meta_profile_snapshot() -> Dict[str, Any]:
    """
    Return a full snapshot of the meta profile for logging or debugging.
    """
    return META_PROFILE.snapshot()
