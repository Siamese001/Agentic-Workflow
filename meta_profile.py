# FILE: meta_profile.py
"""
Unified Meta Profile (v10_10) — ADAPTIVE BIAS ENGINE (REFACTORED)

This module implements the "Subconscious" of the agent (Pillar 5).
It holds long-term memory of performance and safety trends, tuning the
behavior of L1/L2/L5 dynamically.

Responsibilities:
    1. Store Biases: Routing, Planning, QA, Safety preferences.
    2. Process Feedback: Update biases based on Observability spans/summaries.
    3. Provide Snapshots: Allow Observability to log the state of the "Brain".

Refactor Highlights (v10_10):
    • Typed Inputs: Consumes Pydantic `TraceSpan` and `RunSummary` data.
    • Threshold Logic: Centralized heuristics for when to flip biases.
"""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field

# =============================================================================
# DATA MODELS (Biases)
# =============================================================================

class RoutingBias(BaseModel):
    """Preferences for LLM Gateway routing."""
    prefer_fast: bool = False
    prefer_robust_retrieval: bool = False
    prefer_long_context: bool = False


class PlanningBias(BaseModel):
    """Preferences for L1 Cognitive Planning."""
    conservative: bool = False          # Prefer ToT, more checks
    exploratory: bool = False           # Prefer CoT, more branches
    deterministic_recovery: bool = False # Prefer fixed recovery paths


class QaBias(BaseModel):
    """Preferences for QA rigor."""
    recent_failures: bool = False       # Trigger deeper QA
    require_extra_pass: bool = False    # Double-check outputs


class SafetyBias(BaseModel):
    """Preferences for L5 Safety thresholds."""
    heightened_caution: bool = False    # Force STRICT mode
    human_review_important: bool = False # Trigger HIL more often


class MetaProfile(BaseModel):
    """
    Global Adaptive State.
    """
    routing_bias: RoutingBias = Field(default_factory=RoutingBias)
    planning_bias: PlanningBias = Field(default_factory=PlanningBias)
    qa_bias: QaBias = Field(default_factory=QaBias)
    safety_bias: SafetyBias = Field(default_factory=SafetyBias)
    
    # History for debugging/provenance
    update_log: List[Dict[str, Any]] = Field(default_factory=list)

    def snapshot(self) -> Dict[str, Any]:
        return self.model_dump()

    def record_update(self, source: str, changes: Dict[str, Any]) -> None:
        if changes:
            self.update_log.append({
                "source": source,
                "changes": changes,
                "timestamp": "iso-timestamp-placeholder" # In prod use real time
            })
            # Trim log
            if len(self.update_log) > 50:
                self.update_log.pop(0)

# Global Singleton
META_PROFILE = MetaProfile()


# =============================================================================
# READ ACCESSORS (Used by L1/L5/Gateway)
# =============================================================================

def get_routing_bias() -> Dict[str, Any]:
    return META_PROFILE.routing_bias.model_dump()

def get_planning_bias() -> Dict[str, Any]:
    return META_PROFILE.planning_bias.model_dump()

def get_qa_bias() -> Dict[str, Any]:
    return META_PROFILE.qa_bias.model_dump()

def get_safety_bias() -> Dict[str, Any]:
    return META_PROFILE.safety_bias.model_dump()

def get_meta_profile_snapshot() -> Dict[str, Any]:
    return META_PROFILE.snapshot()


# =============================================================================
# WRITE / UPDATE LOGIC (Used by Observability)
# =============================================================================

def update_from_spans(spans: List[Any]) -> None:
    """
    Heuristic: If Planning is > 2x Execution time, assume we are over-thinking
    or the model is too slow, so flip to 'prefer_fast'.
    """
    # spans is list of TraceSpan (Pydantic)
    planning_ms = 0.0
    execution_ms = 0.0

    for s in spans:
        if s.name == "planning":
            planning_ms = s.duration_ms()
        elif s.name == "execution":
            execution_ms = s.duration_ms()

    changes = {}
    
    # Threshold: If Planning is dominant, maybe we need faster inference
    if planning_ms > 0 and execution_ms > 0:
        if planning_ms > (execution_ms * 1.5):
            if not META_PROFILE.routing_bias.prefer_fast:
                META_PROFILE.routing_bias.prefer_fast = True
                changes["routing_bias.prefer_fast"] = True
        else:
             if META_PROFILE.routing_bias.prefer_fast:
                META_PROFILE.routing_bias.prefer_fast = False
                changes["routing_bias.prefer_fast"] = False
    
    META_PROFILE.record_update("spans", changes)


def update_from_run_summary(summary_dict: Dict[str, Any]) -> None:
    """
    Heuristic: High failure rates trigger conservative/caution modes.
    """
    issues = summary_dict.get("issues", {})
    changes = {}

    # 1. Safety Issues -> Heightened Caution
    safety_issues = issues.get("safety", [])
    if len(safety_issues) > 0:
        if not META_PROFILE.safety_bias.heightened_caution:
            META_PROFILE.safety_bias.heightened_caution = True
            changes["safety_bias.heightened_caution"] = True
    else:
        # Cool down if no issues
        if META_PROFILE.safety_bias.heightened_caution:
            META_PROFILE.safety_bias.heightened_caution = False
            changes["safety_bias.heightened_caution"] = False

    # 2. QA Issues -> Conservative Planning
    qa_issues = issues.get("qa", [])
    if len(qa_issues) > 0:
        if not META_PROFILE.planning_bias.conservative:
            META_PROFILE.planning_bias.conservative = True
            changes["planning_bias.conservative"] = True
    
    META_PROFILE.record_update("run_summary", changes)
