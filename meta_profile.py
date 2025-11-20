# FILE: 10_10/meta_profile.py
"""
Meta Profile & Adaptive Biases (v10_10 · Phase 0) — META LAYER ONLY
===================================================================

This module defines the *meta-layer* profile for the agentic system.

It is **NOT** part of L1–L5. It provides SOFT BIASES and historical
signals that L1, L2, routing, and self-correction may consult:

    • Model routing preferences (prefer fast vs robust).
    • Planning preferences (conservative vs exploratory).
    • QA-related hints (recent failure rates, extra passes).
    • Safety-related hints (heightened caution, HIL bias).
    • Rolling statistics (QA failures, correction usage).

Phase 0 objectives:
    • Provide a **deterministic**, in-memory MetaProfile that:
        – can be snapshotted and passed into ExecutionContext
        – influences routing (e.g., prefers_anthropic / prefers_openai)
        – exposes QA / correction failure rates
    • Keep it META-LAYER ONLY:
        – no L1–L5 imports
        – no network calls
        – no side-effects beyond local in-memory state

Compatibility requirements:
    • Preserve `MetaProfileSnapshot` type for existing v10_10 modules:
        – l1.py
        – cognitive_agents.py
        – routing.py
    • Keep helper accessors:
        – get_routing_bias()
        – get_planning_bias()
        – get_qa_bias()
        – get_safety_bias()

Later phases (3–4) may:
    • Wire meta_profile feedback into:
        – routing decisions,
        – reasoning selector,
        – safety bundle choice,
        – execution profile selection.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any

from .models import ReasoningMode


# ======================================================================
# CORE BIAS STRUCTS
# ======================================================================


@dataclass
class RoutingBias:
    """
    Routing preferences and signals.

    • prefers_anthropic / prefers_openai:
        – Soft hint to routing provider selection.
    • prefers_fast_models:
        – Soft hint for latency vs robustness.
    """

    prefers_anthropic: bool = False
    prefers_openai: bool = True
    prefers_fast_models: bool = False


@dataclass
class PlanningBias:
    """
    Planning preferences at the meta level.

    • reasoning_mode_hint:
        – A soft suggestion for ReasoningSelector.
    • conservative_planning:
        – Fewer steps, shallower exploration.
    • exploratory_planning:
        – More steps, deeper exploration.
    """

    reasoning_mode_hint: ReasoningMode = ReasoningMode.COT
    conservative_planning: bool = False
    exploratory_planning: bool = False


@dataclass
class QABias:
    """
    Biases related to QA behavior.

    • extra_qa_passes:
        – Encourages more QA passes when true.
    • reinforce_strictness:
        – Encourages stricter QA interpretation.
    """

    extra_qa_passes: bool = False
    reinforce_strictness: bool = False


@dataclass
class SafetyBias:
    """
    Biases related to safety behavior.

    • elevated_caution:
        – Ask safety to be more conservative.
    • hil_preferred:
        – Prefer HIL escalation for borderline cases.
    """

    elevated_caution: bool = False
    hil_preferred: bool = False


# ======================================================================
# META PROFILE & SNAPSHOT
# ======================================================================


@dataclass
class MetaProfile:
    """
    Full meta-profile state for the system (in-memory, mutable).

    This is a long-lived object that accumulates rolling statistics
    across workflows; snapshots are created per workflow.
    """

    # Current "active" profile id (e.g., RESUME_HIGH_QUALITY, OUTREACH_QUICK)
    active_profile_id: str = "RESUME_HIGH_QUALITY"

    routing_bias: RoutingBias = RoutingBias()
    planning_bias: PlanningBias = PlanningBias()
    qa_bias: QABias = QABias()
    safety_bias: SafetyBias = SafetyBias()

    # Rolling counters for QA / correction behavior
    qa_total_last_10: int = 0
    qa_failures_last_10: int = 0
    corrections_total_last_10: int = 0
    corrections_applied_last_10: int = 0

    def qa_failure_rate(self) -> float:
        if self.qa_total_last_10 == 0:
            return 0.0
        return self.qa_failures_last_10 / float(self.qa_total_last_10)

    def correction_apply_rate(self) -> float:
        if self.corrections_total_last_10 == 0:
            return 0.0
        return self.corrections_applied_last_10 / float(self.corrections_total_last_10)


@dataclass(frozen=True)
class MetaProfileSnapshot:
    """
    Read-only snapshot of the MetaProfile, passed into ExecutionContext
    and used by routing, L1, cognitive agents, etc.

    Existing v10_10 callsites expect:
        • prefers_anthropic
        • prefers_openai
        • qa_failure_rate_last_10
        • correction_rate_last_10
    """

    active_profile_id: str

    prefers_anthropic: bool
    prefers_openai: bool
    prefers_fast_models: bool

    reasoning_mode_hint: str

    qa_failure_rate_last_10: float
    correction_rate_last_10: float

    extra_qa_passes: bool
    reinforce_strictness: bool

    elevated_caution: bool
    hil_preferred: bool


# ======================================================================
# META PROFILE UPDATER (SINGLETON)
# ======================================================================


class MetaProfileUpdater:
    """
    Simple, deterministic meta-profile updater.

    Phase 0:
        • Keeps counters for QA outcomes and corrections.
        • Updates soft routing/planning/QA/safety biases.
    """

    def __init__(self) -> None:
        self.profile = MetaProfile()

    # ---------- snapshot API ----------

    def snapshot(self) -> MetaProfileSnapshot:
        p = self.profile
        return MetaProfileSnapshot(
            active_profile_id=p.active_profile_id,
            prefers_anthropic=p.routing_bias.prefers_anthropic,
            prefers_openai=p.routing_bias.prefers_openai,
            prefers_fast_models=p.routing_bias.prefers_fast_models,
            reasoning_mode_hint=p.planning_bias.reasoning_mode_hint.value,
            qa_failure_rate_last_10=p.qa_failure_rate(),
            correction_rate_last_10=p.correction_apply_rate(),
            extra_qa_passes=p.qa_bias.extra_qa_passes,
            reinforce_strictness=p.qa_bias.reinforce_strictness,
            elevated_caution=p.safety_bias.elevated_caution,
            hil_preferred=p.safety_bias.hil_preferred,
        )

    # ---------- update API ----------

    def set_active_profile(self, profile_id: str) -> None:
        self.profile.active_profile_id = profile_id

    def register_qa_outcome(self, success: bool) -> None:
        """
        Update QA rolling stats and QA/Safety bias hints.
        """
        p = self.profile
        p.qa_total_last_10 = min(10, p.qa_total_last_10 + 1)
        if not success:
            p.qa_failures_last_10 = min(10, p.qa_failures_last_10 + 1)

        # Soft rule: if QA failure rate > 0.4, encourage extra QA passes.
        if p.qa_failure_rate() > 0.4:
            p.qa_bias.extra_qa_passes = True
            p.qa_bias.reinforce_strictness = True
            p.safety_bias.elevated_caution = True
        else:
            p.qa_bias.extra_qa_passes = False
            p.qa_bias.reinforce_strictness = False
            p.safety_bias.elevated_caution = False

    def register_correction(self, applied: bool) -> None:
        """
        Update correction stats and bias toward more conservative planning.
        """
        p = self.profile
        p.corrections_total_last_10 = min(10, p.corrections_total_last_10 + 1)
        if applied:
            p.corrections_applied_last_10 = min(10, p.corrections_applied_last_10 + 1)

        # Soft rule: if we keep correcting, nudge planning toward conservative.
        if p.correction_apply_rate() > 0.3:
            p.planning_bias.conservative_planning = True
            p.planning_bias.exploratory_planning = False
        else:
            p.planning_bias.conservative_planning = False

    def register_provider_choice(self, provider: str) -> None:
        """
        Update routing bias based on provider choices.
        """
        p = self.profile
        if provider.lower().startswith("anthropic"):
            p.routing_bias.prefers_anthropic = True
            p.routing_bias.prefers_openai = False
        elif provider.lower().startswith("openai"):
            p.routing_bias.prefers_openai = True
            p.routing_bias.prefers_anthropic = False

    def set_reasoning_hint(self, mode: ReasoningMode) -> None:
        self.profile.planning_bias.reasoning_mode_hint = mode

    def reset(self) -> None:
        self.profile = MetaProfile()


# Singleton updater instance.
_META_UPDATER = MetaProfileUpdater()


# ======================================================================
# PUBLIC API
# ======================================================================

def get_meta_profile_snapshot() -> MetaProfileSnapshot:
    """
    Return a read-only MetaProfileSnapshot for injection into ExecutionContext.
    """
    return _META_UPDATER.snapshot()


def register_qa_outcome(success: bool) -> None:
    _META_UPDATER.register_qa_outcome(success)


def register_correction(applied: bool) -> None:
    _META_UPDATER.register_correction(applied)


def register_provider_choice(provider: str) -> None:
    _META_UPDATER.register_provider_choice(provider)


def set_active_profile(profile_id: str) -> None:
    _META_UPDATER.set_active_profile(profile_id)


def set_reasoning_hint(mode: ReasoningMode) -> None:
    _META_UPDATER.set_reasoning_hint(mode)


def reset_meta_profile() -> None:
    _META_UPDATER.reset()


# ----------------------------------------------------------------------
# Legacy-style bias accessors (used in comments / possible callsites).
# These return dicts, matching earlier "asdict(profile.*_bias)" patterns.
# ----------------------------------------------------------------------


def get_routing_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.routing_bias)


def get_planning_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.planning_bias)


def get_qa_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.qa_bias)


def get_safety_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.safety_bias)
