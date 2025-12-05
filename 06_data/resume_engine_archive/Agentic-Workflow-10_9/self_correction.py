# FILE: self_correction.py
"""
Unified Self-Correction Surfaces (v10_9 REFACTORED) — META LAYER ONLY

This module defines the unified self-correction framework for the v10_9
agentic architecture. It implements:

    • Canonical self-correction surfaces (RAG_RETRY, QA_RECHECK, etc.)
    • Deterministic error detection rules over state snapshots
    • Enterprise-ordered surface selection (safety > QA > RAG > strategy > checkpoint)
    • Structured correction directives (for L3 / meta-learning)
    • Multi-surface analysis for diagnostics
    • Utilities for telemetry and state patches (read-only)

❗ STRICT GUARDRAILS (META-ONLY):
    • NO L1 (planning)
    • NO L2 (execution / LLM / retrieval)
    • NO L3 (orchestration)
    • NO L4 (state mutation)
    • NO L5 (policy/safety decisions)

All functions operate ONLY on finalized state snapshots and produce
recommendations — they NEVER perform workflow actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models import SelfCorrectionSurface, SafetyIssue


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
    Low-level signal that a correction may be needed.
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
    Normalized recommendation for downstream layers.

    Fields:
        • needed:   whether a correction should be triggered
        • surface:  one of SELF_CORRECTION_SURFACES
        • rationale: human-readable explanation
        • metadata: structured supporting info
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
    Detect whether retrieval was insufficient.
    """
    rag_block = state.get("rag_result") or {}
    docs = rag_block.get("documents") or []

    # v10_9 RAGExecutor returns RAGExecutionPayload.to_dict() under .documents
    if not isinstance(docs, list):
        return None

    # No evidence retrieved → retry
    if len(docs) == 0:
        return CorrectionSignal(
            surface=SelfCorrectionSurface.RAG_RETRY.value,
            reason="No RAG evidence retrieved.",
            metadata={"retrieved_count": 0},
        )

    # Insufficient depth
    if len(docs) < 2:
        return CorrectionSignal(
            surface=SelfCorrectionSurface.RAG_RETRY.value,
            reason="Insufficient RAG evidence depth.",
            metadata={"retrieved_count": len(docs)},
        )

    return None


def _detect_qa_errors(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect failed QA checks.
    """
    qa_block = state.get("qa_result") or {}
    report = qa_block.get("report") or qa_block
    issues = report.get("issues", [])

    # issues = list[dict] from QAReport.to_dict()
    if issues:
        return CorrectionSignal(
            surface=SelfCorrectionSurface.QA_RECHECK.value,
            reason="One or more QA checks failed.",
            metadata={"issues": issues},
        )
    return None


def _detect_strategy_errors(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect that L1 strategy recommended revision.

    NOTE:
        In the refactored system, L2 StrategyExecutor emits:
             payload.aggregated_decision
             payload.aggregated_confidence
             payload.aggregated_rationale
        (Wrapped under state["strategy_result"]["payload"])
    """
    strat_state = state.get("strategy_result") or {}
    payload = strat_state.get("payload") or strat_state

    decision = str(payload.get("aggregated_decision", "")).lower()
    if decision == "revise":
        return CorrectionSignal(
            surface=SelfCorrectionSurface.STRATEGY_REPLAN.value,
            reason="Strategy evaluation signaled a revision.",
            metadata={
                "aggregated_confidence": payload.get("aggregated_confidence"),
                "aggregated_rationale": payload.get("aggregated_rationale"),
            },
        )
    return None


def _detect_safety_halt(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect safety failures requiring human escalation.

    New v10_9 safety format:
        state["safety_result"] = SafetyExecutionPayload.to_dict()
        → {"report": {"issues": [SafetyIssue dicts], ...}}
    """
    safety = state.get("safety_result") or {}
    report = safety.get("report") or safety
    issues = report.get("issues", [])

    for issue in issues:
        # SafetyIssue is a dict after to_dict()
        if isinstance(issue, dict):
            cat = str(issue.get("category", "")).lower()
            msg = str(issue.get("message", "")).lower()
        else:
            # raw string fallback (rare)
            cat = str(issue).lower()
            msg = str(issue).lower()

        # PII → immediate HIL escalation
        if "pii" in cat or "pii" in msg:
            return CorrectionSignal(
                surface=SelfCorrectionSurface.HIL_ESCALATION.value,
                reason="Safety detected PII — escalate to human review.",
                metadata={"issues": issues},
            )

    return None


def _detect_checkpoint_recovery(state: Dict[str, Any]) -> Optional[CorrectionSignal]:
    """
    Detect if the last checkpoint indicates workflow failure.
    """
    checkpoints = state.get("checkpoints") or []
    if not checkpoints:
        return None

    last = checkpoints[-1]
    phase = str(last.get("phase", "")).lower()

    if phase in ("failed", "error"):
        return CorrectionSignal(
            surface=SelfCorrectionSurface.CHECKPOINT_RECOVERY.value,
            reason="Last checkpoint was recorded during failed/error state.",
            metadata={"last_checkpoint": last},
        )
    return None


# ============================================================================
# 4. SURFACE SELECTION LOGIC (ENTERPRISE PRIORITY ORDER)
# ============================================================================

def analyze_state_for_correction(state: Dict[str, Any]) -> CorrectionRecommendation:
    """
    Priority-ordered correction analysis:

        1. Safety → HIL escalation
        2. QA recheck
        3. RAG retry
        4. Strategy replan
        5. Checkpoint recovery

    If no issues → needed=False
    """

    detectors = [
        _detect_safety_halt,
        _detect_qa_errors,
        _detect_rag_errors,
        _detect_strategy_errors,
        _detect_checkpoint_recovery,
    ]

    for detect in detectors:
        sig = detect(state)
        if sig:
            return CorrectionRecommendation(
                needed=True,
                surface=sig.surface,
                rationale=sig.reason,
                metadata=sig.metadata,
            )

    return CorrectionRecommendation(needed=False)


# ============================================================================
# 5. MULTI-SURFACE ANALYSIS (ALL SIGNALS)
# ============================================================================

def analyze_all_surfaces(state: Dict[str, Any]) -> List[CorrectionSignal]:
    """
    Return ALL applicable correction signals, sorted by enterprise priority.

    Useful for:
        • Meta-learning
        • Telemetry
        • Debugging
        • State inspection
    """
    detectors = [
        _detect_safety_halt,
        _detect_qa_errors,
        _detect_rag_errors,
        _detect_strategy_errors,
        _detect_checkpoint_recovery,
    ]

    signals: List[CorrectionSignal] = []
    for detect in detectors:
        sig = detect(state)
        if sig:
            signals.append(sig)

    return signals


# ============================================================================
# 6. FORMATTERS (PATCH + METADATA)
# ============================================================================

def to_patch_dict(rec: CorrectionRecommendation) -> Dict[str, Any]:
    """
    Convert CorrectionRecommendation to a dict suitable for
    state insertion under key "self_correction" by L4.StateAdapter.
    """
    return {"self_correction": rec.to_dict()}


def to_metadata_block(rec: CorrectionRecommendation) -> Dict[str, Any]:
    """
    Convert CorrectionRecommendation into simplified metadata for
    telemetry/meta-learning.
    """
    return {
        "surface": rec.surface,
        "needed": rec.needed,
        "rationale": rec.rationale,
        "metadata": dict(rec.metadata),
    }
