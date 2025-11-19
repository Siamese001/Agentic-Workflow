# FILE: self_correction.py
"""
Unified Self-Correction Layer (v10_9, Refactored — META ONLY)

This module implements a fully deterministic, enterprise-grade
self-correction framework **strictly at the META layer**.

It restores ALL missing 10_8 functionality:
    • Multi-surface detection (RAG_RETRY, QA_RECHECK, STRATEGY_REPLAN,
      HIL_ESCALATION, CHECKPOINT_RECOVERY)
    • Structured CorrectionSignal + CorrectionRecommendation models
    • Resume-aware + JD-aware QA/RAG error detectors
    • Surface-priority ordering (safety → qa → rag → strategy → recovery)
    • Multi-surface analysis for diagnostics
    • Patch serialization helpers
    • Telemetry-friendly metadata blocks

Strict L1–L5 purity:
    • NO planning (L1)
    • NO execution (L2)
    • NO orchestration (L3)
    • NO state mutation (L4)
    • NO safety/policy (L5)
    • META-only deterministic analysis of state snapshots
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
    Low-level signal indicating a correction opportunity.
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
    High-level, normalized recommendation for L3 arbitration/meta-learning.
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
# 3. ERROR SIGNAL DETECTORS (pure, deterministic)
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
    safety = (state.get("safety_result") or {}).get("report") or {}
    issues = safety.get("issues", [])
    for iss in issues:
        code = ""
        if isinstance(iss, dict):
            code = str(iss.get("code", ""))
        else:
            code = str(iss)
        if "pii" in code.lower() or "forbidden" in code.lower() or "prompt_injection" in code.lower():
            return CorrectionSignal(
                surface=SelfCorrectionSurface.HIL_ESCALATION.value,
                reason="Safety flagged sensitive content requiring human review.",
                metadata={"safety_issues": issues},
            )
    return None


def _detect_checkpoint_recovery(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    checks = state.get("checkpoints") or []
    if not checks:
        return None
    last = checks[-1]
    phase = str(last.get("phase", "")).lower()
    if phase in ("failed", "error"):
        return CorrectionSignal(
            surface=SelfCorrectionSurface.CHECKPOINT_RECOVERY.value,
            reason="Last checkpoint created during failed/error state.",
            metadata={"last_checkpoint": last},
        )
    return None


# ============================================================================
# 4. SURFACE SELECTION LOGIC (priority ordered)
# ============================================================================

def analyze_state_for_correction(state: Dict[str, Any]) -> CorrectionRecommendation:
    """
    Priority order (enterprise standard):

        1. Safety → HIL escalation
        2. QA → recheck
        3. RAG → retry
        4. Strategy → replan
        5. Recovery → checkpoint restore
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
# 5. MULTI-SURFACE ANALYSIS (diagnostics & meta-learning)
# ============================================================================

def analyze_all_surfaces(state: Dict[str, Any]) -> List[CorrectionSignal]:
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
# 6. FORMATTERS (L3/L4 & Telemetry)
# ============================================================================

def to_patch_dict(rec: CorrectionRecommendation) -> Dict[str, Any]:
    """
    Convert a CorrectionRecommendation into a structure suitable for
    L4.StatePatch under key "self_correction".
    """
    return {"self_correction": rec.to_dict()}


def to_metadata_block(rec: CorrectionRecommendation) -> Dict[str, Any]:
    """
    Telemetry/log-friendly metadata block.
    """
    return {
        "surface": rec.surface,
        "needed": rec.needed,
        "rationale": rec.rationale,
        "metadata": rec.metadata,
    }
