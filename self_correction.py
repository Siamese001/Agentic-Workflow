# FILE: self_correction.py
"""
Unified Self-Correction Surfaces (v10_9) — META LAYER ONLY

This module defines the unified self-correction framework for the v10_9
agentic architecture. It implements:

    • Canonical self-correction surfaces (RAG_RETRY, QA_RECHECK, etc.)
    • Deterministic error detection rules over state snapshots
    • Surface selection heuristics (which surface should fire)
    • Structured correction directives (for L3 / meta-learning)
    • Multi-surface analysis for diagnostics
    • Formatting helpers for state patches & telemetry

Layer Guardrails:

    • NO L1 cognition (no planning or PlanObject creation).
    • NO L2 execution (no tool/LLM calls).
    • NO L3 orchestration (no DAG/phase control).
    • NO L4 state mutation (no StateAdapter usage).
    • NO L5 safety/policy decisions.

Everything here is pure META logic that reads finalized state snapshots
and produces *recommendations* for other layers to act on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models import SelfCorrectionSurface


# ============================================================================
# 1. CANONICAL SURFACE DEFINITIONS
# ============================================================================

SELF_CORRECTION_SURFACES = {
    SelfCorrectionSurface.RAG_RETRY.value,
    SelfCorrectionSurface.QA_RECHECK.value,
    SelfCorrectionSurface.STRATEGY_REPLAN.value,
    SelfCorrectionSurface.HIL_ESCALATION.value,
    SelfCorrectionSurface.CHECKPOINT_RECOVERY.value,
}


# ============================================================================
# 2. SELF-CORRECTION RESULT OBJECTS
# ============================================================================


@dataclass
class CorrectionSignal:
    """
    A low-level signal that a correction may be needed.

    Fields:
        • surface: which correction surface is applicable
        • reason: short human-readable explanation
        • metadata: optional structured info (e.g., failing checks, missing evidence)

    This is used internally and can also be logged as-is for diagnostics.
    """

    surface: str
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface": self.surface,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


@dataclass
class CorrectionRecommendation:
    """
    A normalized self-correction recommendation for L3 arbitrators
    and meta-learning.

    Fields:
        • needed: bool
        • surface: one of SELF_CORRECTION_SURFACES
        • rationale: why correction is needed
        • metadata: structured breakdown (issues, counts, etc.)

    This object is PURELY advisory. It does NOT execute retries/replans;
    L3/L5 and meta layers decide how/when to react.
    """

    needed: bool
    surface: Optional[str] = None
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "needed": self.needed,
            "surface": self.surface,
            "rationale": self.rationale,
            "metadata": dict(self.metadata),
        }


# ============================================================================
# 3. ERROR SIGNAL DETECTORS (STATE-BASED, PURE)
# ============================================================================

def _detect_rag_errors(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect RAG-related issues that might warrant a RAG_RETRY surface.
    """
    rag = state.get("rag_result") or {}
    docs = rag.get("documents") or []
    if len(docs) == 0:
        return CorrectionSignal(
            surface=SelfCorrectionSurface.RAG_RETRY.value,
            reason="No evidence retrieved.",
            metadata={"retrieved_count": 0},
        )
    if len(docs) < 2:
        return CorrectionSignal(
            surface=SelfCorrectionSurface.RAG_RETRY.value,
            reason="Insufficient evidence depth.",
            metadata={"retrieved_count": len(docs)},
        )
    return None


def _detect_qa_errors(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect QA-related issues that might warrant a QA_RECHECK surface.
    """
    qa = (state.get("qa_result") or {}).get("report") or {}
    issues = qa.get("issues", [])
    if issues:
        return CorrectionSignal(
            surface=SelfCorrectionSurface.QA_RECHECK.value,
            reason="QA checks failed.",
            metadata={"issues": issues},
        )
    return None


def _detect_strategy_errors(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect strategy-related issues that might warrant a STRATEGY_REPLAN.
    """
    strat = state.get("strategy_result") or {}
    decision_block = strat.get("decision") or {}
    aggregated_decision = str(decision_block.get("aggregated_decision") or "").lower()
    if aggregated_decision == "revise":
        return CorrectionSignal(
            surface=SelfCorrectionSurface.STRATEGY_REPLAN.value,
            reason="Strategy planner signaled revision.",
            metadata={
                "aggregated_rationale": decision_block.get("aggregated_rationale", ""),
                "aggregated_confidence": decision_block.get("aggregated_confidence", 0.0),
            },
        )
    return None


def _detect_safety_halt(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect safety-related issues that might require HIL_ESCALATION.

    Heuristic:
        • If ANY issue code contains "pii", escalate to HIL.
    """
    safety = (state.get("safety_result") or {}).get("report") or {}
    issues = safety.get("issues", [])
    # issues here are typically list[SafetyIssue dict-like]
    for iss in issues:
        code = ""
        if isinstance(iss, dict):
            code = str(iss.get("code", ""))
        else:
            code = str(iss)
        if "pii" in code.lower():
            return CorrectionSignal(
                surface=SelfCorrectionSurface.HIL_ESCALATION.value,
                reason="Safety flagged sensitive content requiring human review.",
                metadata={"safety_issues": issues},
            )
    return None


def _detect_checkpoint_recovery(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect if the last checkpoint was created during an error/failed phase,
    suggesting CHECKPOINT_RECOVERY.
    """
    checks = state.get("checkpoints") or []
    if not checks:
        return None
    last = checks[-1]
    phase = str(last.get("phase", "")).lower()
    if phase in ("failed", "error"):
        return CorrectionSignal(
            surface=SelfCorrectionSurface.CHECKPOINT_RECOVERY.value,
            reason="Last checkpoint created during error/failed state.",
            metadata={"last_checkpoint": last},
        )
    return None


# ============================================================================
# 4. SURFACE SELECTION LOGIC
# ============================================================================

def analyze_state_for_correction(state: Dict[str, Any]) -> CorrectionRecommendation:
    """
    Evaluate state for ANY known correction surfaces.
    Returns the first applicable correction recommendation.

    Priority order (enterprise preference):

        1. Safety → HIL escalation
        2. QA recheck
        3. RAG retry
        4. Strategy replan
        5. Checkpoint recovery

    If no signals are found:
        return CorrectionRecommendation(needed=False).
    """
    detectors = [
        _detect_safety_halt,
        _detect_qa_errors,
        _detect_rag_errors,
        _detect_strategy_errors,
        _detect_checkpoint_recovery,
    ]

    for detector in detectors:
        signal = detector(state)
        if signal:
            return CorrectionRecommendation(
                needed=True,
                surface=signal.surface,
                rationale=signal.reason,
                metadata=signal.metadata,
            )

    return CorrectionRecommendation(needed=False)


# ============================================================================
# 5. MULTI-SURFACE ANALYSIS (FOR DIAGNOSTICS / META-LEARNING)
# ============================================================================

def analyze_all_surfaces(state: Dict[str, Any]) -> List[CorrectionSignal]:
    """
    Return ALL detected correction signals, not just the first one.

    Useful for:
        • Meta-learning / analytics
        • Telemetry
        • Offline diagnostics
    """
    signals: List[CorrectionSignal] = []

    for detector in [
        _detect_rag_errors,
        _detect_qa_errors,
        _detect_strategy_errors,
        _detect_safety_halt,
        _detect_checkpoint_recovery,
    ]:
        sig = detector(state)
        if sig:
            signals.append(sig)

    return signals


# ============================================================================
# 6. FORMATTERS FOR L3/L4/L5 / TELEMETRY
# ============================================================================

def to_patch_dict(rec: CorrectionRecommendation) -> Dict[str, Any]:
    """
    Convert a CorrectionRecommendation to a dict suitable for inclusion
    in state via StatePatch under key "self_correction".

    Example usage (from L3 Orchestrator):

        sc_rec = analyze_state_for_correction(state_adapter.state)
        sc_patch = to_patch_dict(sc_rec)
        state_adapter.apply_patch(StatePatch(key="self_correction",
                                             value=sc_patch["self_correction"]))
    """
    return {"self_correction": rec.to_dict()}


def to_metadata_block(rec: CorrectionRecommendation) -> Dict[str, Any]:
    """
    Convert a CorrectionRecommendation into a standardized metadata block
    for telemetry, logs, or meta-learning.

    Shape:
        {
          "surface":  <surface or None>,
          "needed":   bool,
          "rationale": str,
          "metadata":  { ... },
        }
    """
    return {
        "surface": rec.surface,
        "needed": rec.needed,
        "rationale": rec.rationale,
        "metadata": rec.metadata,
    }
