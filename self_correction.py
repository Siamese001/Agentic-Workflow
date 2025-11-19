# FILE: self_correction.py
"""
Unified Self-Correction Surfaces (v10_9) — ENTERPRISE MODULE

This module defines the unified self-correction framework for the v10_9
agentic architecture. It implements:

    • Canonical self-correction surfaces (RAG_RETRY, QA_RECHECK, etc.)
    • Deterministic error detection rules
    • Surface selection heuristics
    • Structured correction directives (used by L3 ArbitrationEngine)
    • Optional multi-step escalation (HIL, Replan, Halt)
    • Outcome reporting for telemetry & meta-learning

This sits ENTIRELY ABOVE L1–L5:

    • L1 produces plan.reasoning & injection metadata.
    • L2 produces execution_result payloads.
    • L3 ArbitrationEngine & DAG decide actions.
    • L4 applies only the state patches L3 chooses.
    • L5 makes policy decisions (risk, retry, block).

self_correction.py is a META-LAYER “advisor” — it **never** mutates state.
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
    A signal that a correction is needed.

    Fields:
        • surface: which correction surface is applicable
        • reason: short human-readable explanation
        • metadata: optional structured info (e.g., failing checks, missing evidence)
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
    A normalized self-correction recommendation for L3 arbitrators.

    Fields:
        • needed: bool
        • surface: one of SELF_CORRECTION_SURFACES
        • rationale: why correction is needed
        • metadata: structured breakdown
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
# 3. ERROR SIGNAL DETECTORS
# ============================================================================

def _detect_rag_errors(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
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
    strat = state.get("strategy_result") or {}
    decision_block = strat.get("decision") or {}
    rationale = str(decision_block.get("aggregated_decision") or "")
    if rationale.lower() == "revise":
        return CorrectionSignal(
            surface=SelfCorrectionSurface.STRATEGY_REPLAN.value,
            reason="Strategy planner signaled revision.",
            metadata={
                "aggregated_rationale": decision_block.get("aggregated_rationale", "")
            },
        )
    return None


def _detect_safety_halt(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    safety = (state.get("safety_result") or {}).get("report") or {}
    issues = safety.get("issues", [])
    if any("pii" in (iss.get("code", "") or "") for iss in issues):
        return CorrectionSignal(
            surface=SelfCorrectionSurface.HIL_ESCALATION.value,
            reason="Safety flagged sensitive content requiring human review.",
            metadata={"safety_issues": issues},
        )
    return None


def _detect_checkpoint_recovery(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    checks = state.get("checkpoints") or []
    if len(checks) > 0:
        last = checks[-1]
        if last.get("phase") in ("failed", "error"):
            return CorrectionSignal(
                surface=SelfCorrectionSurface.CHECKPOINT_RECOVERY.value,
                reason="Last checkpoint created during error state.",
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

    Priority order (matches enterprise recovery preference):

        1. Safety → HIL escalation
        2. QA recheck
        3. RAG retry
        4. Strategy replan
        5. Checkpoint recovery

    If no signals found:
        return CorrectionRecommendation(needed=False)
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
# 5. MULTI-SURFACE ANALYSIS (for meta-learning)
# ============================================================================

def analyze_all_surfaces(state: Dict[str, Any]) -> List[CorrectionSignal]:
    """
    Return ALL detected correction signals, not just the first one.

    Useful for:
        • Meta-learning  
        • Telemetry  
        • Offline analysis
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
# 6. FORMATTERS FOR L3/L5 CONSUMPTION
# ============================================================================

def to_patch_dict(rec: CorrectionRecommendation) -> Dict[str, Any]:
    """
    Convert a CorrectionRecommendation to a dict suitable for inclusion
    in state via StatePatch under key "self_correction".
    """
    return {"self_correction": rec.to_dict()}


def to_metadata_block(rec: CorrectionRecommendation) -> Dict[str, Any]:
    """
    Convert a CorrectionRecommendation into a metadata block for telemetry.
    """
    return {
        "surface": rec.surface,
        "needed": rec.needed,
        "rationale": rec.rationale,
        "metadata": rec.metadata,
    }
