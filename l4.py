# FILE: 10_10/l4.py
"""
L4 State Adapter — Deterministic Mutation Layer (v10_10)
=======================================================

Responsibilities:
    • Translate L2/L3/L5 outputs into a deterministic, serializable state patch.
    • Capture:
        - Strategy text
        - RAG evidence
        - Drafted sections
        - QA findings
        - Safety findings
        - Correction signals
        - Safety pass/fail flag
    • Remain PURE (no side effects other than observability events).

Non-Responsibilities:
    • No LLM calls.
    • No execution or orchestration.
    • No policy decisions.
    • No persistence (caller decides where/how to store patches).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from models import L2ResultBundle, ExecutionContext
from self_correction import CorrectionSignal
from observability import record_event, record_exception


# =============================================================================
# State Patch Model (local to L4)
# =============================================================================

@dataclass
class StatePatch:
    """
    A minimal, deterministic representation of workflow output and signals.

    This structure is intentionally simple and does NOT perform any I/O;
    it is just a typed container for downstream persistence or inspection.
    """

    strategy_text: str | None = None
    rag_evidence: List[Dict[str, Any]] = field(default_factory=list)
    drafted_sections: List[Dict[str, Any]] = field(default_factory=list)
    qa_findings: List[Dict[str, Any]] = field(default_factory=list)
    safety_findings: List[Dict[str, Any]] = field(default_factory=list)
    correction_signals: List[Dict[str, Any]] = field(default_factory=list)
    safety_passed: bool | None = None


# =============================================================================
# State Adapter API
# =============================================================================

def apply_state_patch(
    l2_results: L2ResultBundle,
    corrections: List[CorrectionSignal],
    ctx: ExecutionContext,
    safety_passed: bool,
) -> Dict[str, Any]:
    """
    Construct a deterministic state patch from a single DAG run.

    Inputs:
        l2_results     — outputs from L2 (strategy, rag, drafting, qa, safety)
        corrections    — correction signals emitted by self_correction surfaces
        ctx            — execution context (used only for observability metadata)
        safety_passed  — final safety gate decision from L5

    Output:
        A plain dict representing the patch to be applied to persistent state.
    """
    span_ctx = ctx.span_context()

    try:
        record_event(
            "l4.apply_state_patch_start",
            {"job_title": span_ctx.get("job_title", ""), "role_type": span_ctx.get("role_type", "")},
        )

        # ---------------------------------------------------------------------
        # STRATEGY
        # ---------------------------------------------------------------------
        strategy_text = l2_results.strategy.get_chosen_branch_text()

        # ---------------------------------------------------------------------
        # RAG EVIDENCE
        # ---------------------------------------------------------------------
        rag_evidence: List[Dict[str, Any]] = [
            {
                "text": ev.text,
                "score": ev.score,
                "source": ev.source,
            }
            for ev in (l2_results.rag.evidence or [])
        ]

        # ---------------------------------------------------------------------
        # DRAFTED SECTIONS
        # ---------------------------------------------------------------------
        drafted_sections: List[Dict[str, Any]] = [
            {
                "title": sec.title,
                "outline": sec.outline,
                "text": sec.text,
                "compliance_notes": sec.compliance_notes,
            }
            for sec in (l2_results.drafting.sections or [])
        ]

        # ---------------------------------------------------------------------
        # QA FINDINGS
        # ---------------------------------------------------------------------
        qa_findings: List[Dict[str, Any]] = [
            {
                "id": chk.id,
                "passed": chk.passed,
                "reason": chk.reason,
                "severity": chk.severity,
            }
            for chk in (l2_results.qa.checks or [])
        ]

        # ---------------------------------------------------------------------
        # SAFETY FINDINGS
        # ---------------------------------------------------------------------
        safety_findings: List[Dict[str, Any]] = [
            {
                "id": f.id,
                "category": f.category,
                "blocking": f.blocking,
                "reason": f.reason,
            }
            for f in (l2_results.safety.findings or [])
        ]

        # ---------------------------------------------------------------------
        # CORRECTION SIGNALS
        # ---------------------------------------------------------------------
        correction_signals: List[Dict[str, Any]] = [
            {
                "surface": sig.surface,
                "severity": sig.severity,
                "reason": sig.reason,
                "recommended_action": sig.recommended_action,
            }
            for sig in (corrections or [])
        ]

        patch = StatePatch(
            strategy_text=strategy_text,
            rag_evidence=rag_evidence,
            drafted_sections=drafted_sections,
            qa_findings=qa_findings,
            safety_findings=safety_findings,
            correction_signals=correction_signals,
            safety_passed=safety_passed,
        )

        record_event(
            "l4.apply_state_patch_complete",
            {
                "safety_passed": safety_passed,
                "num_sections": len(drafted_sections),
                "num_rag_evidence": len(rag_evidence),
                "num_corrections": len(corrections),
            },
        )

        # Return as plain dict for easy serialization/persistence
        return {
            "strategy_text": patch.strategy_text,
            "rag_evidence": patch.rag_evidence,
            "drafted_sections": patch.drafted_sections,
            "qa_findings": patch.qa_findings,
            "safety_findings": patch.safety_findings,
            "correction_signals": patch.correction_signals,
            "safety_passed": patch.safety_passed,
        }

    except Exception as exc:
        record_exception("l4_state_patch_error", exc)
        # Bubble the error up to L3; L4 must not swallow failures silently.
        raise
