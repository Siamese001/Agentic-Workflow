# FILE: 10_10/meta_profile.py
"""
Meta Profile & Adaptive Biases (v10_10 · Phase 3) — META LAYER ONLY
===================================================================

This module defines the *meta-layer* profile for the agentic system.

It is **NOT** part of L1–L5. It provides SOFT BIASES and historical
signals that L1, L2, routing, and self-correction may consult:

    • Model routing preferences (prefer fast vs robust).
    • Planning preferences (conservative vs exploratory).
    • QA-related hints (recent failure rates, extra passes).
    • Safety-related hints (heightened caution, HIL bias).
    • Rolling statistics (QA failures, correction usage).
    • Phase-1: ProfileInferenceResult storage (seniority, domains, skills).

...
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from core.models.models import ProfileInferenceResult

# ======================================================================
# META-PROFILE DATASTRUCTURES
# ======================================================================

@dataclass
class RoutingBias:
    prefer_fast: bool = False
    prefer_robust: bool = False
    last_model_used: Optional[str] = None


@dataclass
class PlanningBias:
    conservative: bool = False
    exploratory: bool = False
    recent_failures: int = 0


@dataclass
class QABias:
    extra_passes: int = 0
    last_confidence: float = 0.0


@dataclass
class SafetyBias:
    heightened_caution: bool = False
    hil_bias: float = 0.0


@dataclass
class MetaProfile:
    """
    Central meta-profile object representing adaptive, soft preferences.

    Phase-1 addition:
    -----------------
    profile_inference : ProfileInferenceResult
        Stores seniority/domain/skills inference from L1 and routes
        into planning/routing for richer Agent Boundaries.
    """
    routing_bias: RoutingBias = field(default_factory=RoutingBias)
    planning_bias: PlanningBias = field(default_factory=PlanningBias)
    qa_bias: QABias = field(default_factory=QABias)
    safety_bias: SafetyBias = field(default_factory=SafetyBias)

    # NEW — restored from v10_9 logic, typed for v10_10
    profile_inference: ProfileInferenceResult = field(
        default_factory=ProfileInferenceResult
    )


@dataclass
class MetaProfileSnapshot:
    """Read-only snapshot of MetaProfile used by L1 and routing.

    This is a *view* over the internal MetaProfile plus derived
    profile inference fields. It must remain backwards compatible
    with existing Phase-3 consumers (L1, routing, cognitive agents).
    """

    # Identity / profile selection
    name: str
    active_profile_id: str = ""

    # Provider / performance preferences
    prefers_anthropic: bool = False
    prefers_openai: bool = True
    prefers_fast_models: bool = False

    # Reasoning / QA / safety signals
    reasoning_mode_hint: Optional[str] = None
    qa_failure_rate_last_10: float = 0.0
    correction_rate_last_10: float = 0.0
    extra_qa_passes: int = 0
    reinforce_strictness: bool = False
    elevated_caution: bool = False
    hil_preferred: bool = False

    # NEW - Phase 1 profile inference (read-only view)
    seniority_label: Optional[str] = None
    domain_label: Optional[str] = None
    skill_cluster_labels: List[str] = field(default_factory=list)


# ======================================================================
# STATE HOLDER (SINGLETON UPDATER)
# ======================================================================

class _MetaUpdater:
    """
    Internal singleton managing mutations to the MetaProfile.
    Legal mutation surface occurs here (L4-compatible).
    """

    def __init__(self):
        self.profile = MetaProfile()

    # -------------------------------
    # PROFILE INFERENCE (NEW - PHASE 1)
    # -------------------------------
    def update_profile_inference(self, inference: ProfileInferenceResult):
        """
        Replace the stored profile inference.
        L1 callers overwrite the entire typed structure.
        """
        self.profile.profile_inference = inference

    def get_profile_inference(self) -> Dict[str, Any]:
        return asdict(self.profile.profile_inference)

    # -------------------------------
    # EXISTING BIASES
    # -------------------------------
    def update_routing(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.profile.routing_bias, k, v)

    def update_planning(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.profile.planning_bias, k, v)

    def update_qa(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.profile.qa_bias, k, v)

    def update_safety(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.profile.safety_bias, k, v)


# ======================================================================
# MODULE-LEVEL SINGLETON
# ======================================================================

_META_UPDATER = _MetaUpdater()


# ======================================================================
# PUBLIC API
# ======================================================================

def set_profile_inference(inference: ProfileInferenceResult):
    _META_UPDATER.update_profile_inference(inference)


def get_profile_inference() -> Dict[str, Any]:
    return _META_UPDATER.get_profile_inference()


def build_meta_profile_snapshot(name: str) -> MetaProfileSnapshot:
    """Construct a typed MetaProfileSnapshot for the given profile name.

    This provides a stable, read-only view for L1 and routing that
    exposes both meta biases and derived profile inference signals.
    """

    profile = _META_UPDATER.profile

    # Routing / provider preferences
    routing = profile.routing_bias
    planning = profile.planning_bias
    qa = profile.qa_bias
    safety = profile.safety_bias

    # Map profile inference into flat snapshot fields.
    inf = profile.profile_inference
    seniority_label: Optional[str] = None
    domain_label: Optional[str] = None
    skill_cluster_labels: List[str] = []

    if inf is not None:
        if inf.seniority is not None:
            seniority_label = inf.seniority.label
        if inf.domain is not None:
            domain_label = inf.domain.primary_label or (inf.domain.labels[0] if inf.domain.labels else None)
        if inf.skills is not None:
            skill_cluster_labels = list(inf.skills.labels or [])

    return MetaProfileSnapshot(
        name=name,
        active_profile_id=name,
        prefers_anthropic=False,
        prefers_openai=True,
        prefers_fast_models=routing.prefer_fast,
        reasoning_mode_hint=None,
        qa_failure_rate_last_10=0.0,
        correction_rate_last_10=0.0,
        extra_qa_passes=qa.extra_passes,
        reinforce_strictness=planning.conservative,
        elevated_caution=safety.heightened_caution,
        hil_preferred=bool(safety.hil_bias and safety.hil_bias > 0.0),
        seniority_label=seniority_label,
        domain_label=domain_label,
        skill_cluster_labels=skill_cluster_labels,
    )


def get_routing_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.routing_bias)


def get_planning_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.planning_bias)


def get_qa_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.qa_bias)


def get_safety_bias() -> Dict[str, Any]:
    return asdict(_META_UPDATER.profile.safety_bias)
