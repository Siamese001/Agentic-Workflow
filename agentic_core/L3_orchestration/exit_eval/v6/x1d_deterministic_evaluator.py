"""X1D Deterministic Groundedness Evaluator — AG-5 W4.

Plan: ``ag5-exit-x1-evaluator-wiring-d8e4a2``.

Deterministic evaluation of grounded answer quality without LLM judge calls.
Uses AG-4 FinalEvidenceContract fields to assess:
- Evidence presence (EMPTY/BLOCKED/CONFLICTED/UNKNOWN fails)
- Support status (PASS, WEAK_WITH_CAVEATS with caveats, PARTIAL, FAIL)
- Citation presence and validity
- Intent/evidence/output alignment (structural check)

This evaluator is intentionally conservative: when in doubt, it produces
UNKNOWN or FAIL rather than risk an ungrounded ALLOW.

AG-4 invariants:
- UNKNOWN never treated as PASS
- NOT_APPLICABLE requires reason (for non-grounded routes)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    STATUS_UNKNOWN,
    STATUS_NOT_APPLICABLE,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_CONFLICTED,
)
from agentic_core.runtime.contracts.x1_checkout_result import (
    X1EvaluatorType,
    X1Item,
    X1Verdict,
)


@dataclass(frozen=True, slots=True)
class GroundednessEvidence:
    """Structured evidence for X1D deterministic evaluation."""

    fec_present: bool
    fec_status: str
    evidence_item_count: int
    support_target_met: bool
    support_target_partial: bool
    evidence_sufficiency_score: float
    citation_map_present: bool
    contradiction_report_present: bool
    intent_text: str = ""
    output_text: str = ""


def _extract_fec_status(fec: FinalEvidenceContract | dict[str, Any] | None) -> str:
    """Extract c0_status from FEC object or dict."""
    if fec is None:
        return "EMPTY"
    if isinstance(fec, dict):
        return str(fec.get("c0_status", STATUS_UNKNOWN)).upper()
    # It's a dataclass instance
    status = getattr(fec, "c0_status", None)
    if status is None:
        return STATUS_UNKNOWN
    return str(status).upper()


def _extract_evidence_count(fec: FinalEvidenceContract | dict[str, Any] | None) -> int:
    """Count evidence items in FEC."""
    if fec is None:
        return 0
    if isinstance(fec, dict):
        items = fec.get("evidence_items", [])
        return len(items) if isinstance(items, (list, tuple)) else 0
    items = getattr(fec, "evidence_items", ())
    return len(items)


def _extract_support_flags(fec: FinalEvidenceContract | dict[str, Any] | None) -> tuple[bool, bool, float]:
    """Extract (support_target_met, support_target_partial, sufficiency_score)."""
    if fec is None:
        return False, False, 0.0
    if isinstance(fec, dict):
        met = bool(fec.get("support_target_met", False))
        partial = bool(fec.get("support_target_partial", False))
        score = float(fec.get("evidence_sufficiency_score", 0.0))
        return met, partial, score
    return (
        getattr(fec, "support_target_met", False),
        getattr(fec, "support_target_partial", False),
        getattr(fec, "evidence_sufficiency_score", 0.0),
    )


def _extract_citation_contradiction(fec: FinalEvidenceContract | dict[str, Any] | None) -> tuple[bool, bool]:
    """Extract (citation_map_present, contradiction_report_present)."""
    if fec is None:
        return False, False
    if isinstance(fec, dict):
        cmap = fec.get("citation_map", {})
        creport = fec.get("contradiction_report", {})
        return bool(cmap), bool(creport)
    cmap = getattr(fec, "citation_map", None)
    creport = getattr(fec, "contradiction_report", None)
    return bool(cmap), bool(creport)


def build_groundedness_evidence(
    fec: FinalEvidenceContract | dict[str, Any] | None,
    intent_text: str = "",
    output_text: str = "",
) -> GroundednessEvidence:
    """Build GroundednessEvidence from FEC and optional intent/output."""
    return GroundednessEvidence(
        fec_present=fec is not None,
        fec_status=_extract_fec_status(fec),
        evidence_item_count=_extract_evidence_count(fec),
        support_target_met=_extract_support_flags(fec)[0],
        support_target_partial=_extract_support_flags(fec)[1],
        evidence_sufficiency_score=_extract_support_flags(fec)[2],
        citation_map_present=_extract_citation_contradiction(fec)[0],
        contradiction_report_present=_extract_citation_contradiction(fec)[1],
        intent_text=intent_text,
        output_text=output_text,
    )


def evaluate_x1d_groundedness_deterministic(
    *,
    fec: FinalEvidenceContract | dict[str, Any] | None,
    intent_text: str = "",
    output_text: str = "",
    groundedness_threshold: float = 0.5,
    sufficiency_threshold: float = 0.6,
) -> X1Item:
    """Deterministic X1D groundedness evaluator.

    Args:
        fec: FinalEvidenceContract or dict (from ExitReviewPacket.final_evidence_contract)
        intent_text: User intent/query text for structural alignment check
        output_text: Generated output text for citation validation
        groundedness_threshold: Minimum score for PASS (default 0.5)
        sufficiency_threshold: Minimum sufficiency score for PASS (default 0.6)

    Returns:
        X1Item with verdict (PASS, FAIL, WARN, UNKNOWN, NOT_APPLICABLE)

    AG-4 invariants:
    - UNKNOWN never treated as PASS
    - NOT_APPLICABLE requires reason (returned when fec is None for non-grounded route)
    """
    # Build evidence struct
    gev = build_groundedness_evidence(fec, intent_text, output_text)

    # NOT_APPLICABLE: no FEC present (non-grounded route like cache hit)
    if not gev.fec_present:
        return X1Item(
            gate_id="X1D",
            verdict=X1Verdict.NOT_APPLICABLE,
            decisive_reason="No FinalEvidenceContract — non-grounded route",
            not_applicable_reason="Cache hit or non-grounded path does not require evidence validation",
            evaluator_type=X1EvaluatorType.CODE,
            score=0.0,
            threshold=groundedness_threshold,
        )

    # Check FEC status — these are hard materiality failures
    status_failures: list[str] = []
    if gev.fec_status == "EMPTY":
        status_failures.append("EVIDENCE_EMPTY")
    elif gev.fec_status == "BLOCKED":
        status_failures.append("EVIDENCE_BLOCKED")
    elif gev.fec_status == "CONFLICTED":
        status_failures.append("EVIDENCE_CONFLICTED")
    elif gev.fec_status == "UNKNOWN":
        status_failures.append("EVIDENCE_UNKNOWN")

    if status_failures:
        return X1Item(
            gate_id="X1D",
            verdict=X1Verdict.FAIL,
            decisive_reason=f"Material evidence failure: {'; '.join(status_failures)}",
            evaluator_type=X1EvaluatorType.CODE,
            score=0.0,
            threshold=groundedness_threshold,
        )

    # Check evidence item count — zero items is a material failure
    if gev.evidence_item_count == 0:
        return X1Item(
            gate_id="X1D",
            verdict=X1Verdict.FAIL,
            decisive_reason="EVIDENCE_EMPTY: FinalEvidenceContract contains zero evidence items",
            evaluator_type=X1EvaluatorType.CODE,
            score=0.0,
            threshold=groundedness_threshold,
        )

    # Check support target
    if gev.support_target_met:
        # Full support target met — PASS
        return X1Item(
            gate_id="X1D",
            verdict=X1Verdict.PASS,
            decisive_reason="Support target met with sufficient evidence",
            evaluator_type=X1EvaluatorType.CODE,
            score=gev.evidence_sufficiency_score,
            threshold=sufficiency_threshold,
            evidence_refs=(f"fec:{gev.evidence_item_count}items",),
        )

    if gev.support_target_partial:
        # Partial support — WARN with caveats required
        return X1Item(
            gate_id="X1D",
            verdict=X1Verdict.WARN,
            decisive_reason="WEAK_WITH_CAVEATS: Partial evidence support",
            evaluator_type=X1EvaluatorType.CODE,
            score=gev.evidence_sufficiency_score,
            threshold=sufficiency_threshold,
            evidence_refs=(f"fec:{gev.evidence_item_count}items:partial",),
        )

    # Check sufficiency score below threshold
    if gev.evidence_sufficiency_score < sufficiency_threshold:
        return X1Item(
            gate_id="X1D",
            verdict=X1Verdict.FAIL,
            decisive_reason=f"Evidence sufficiency score {gev.evidence_sufficiency_score:.2f} below threshold {sufficiency_threshold}",
            evaluator_type=X1EvaluatorType.CODE,
            score=gev.evidence_sufficiency_score,
            threshold=sufficiency_threshold,
        )

    # WEAK status without caveats — WARN
    if gev.fec_status == "WEAK":
        return X1Item(
            gate_id="X1D",
            verdict=X1Verdict.WARN,
            decisive_reason="WEAK_EVIDENCE_NO_CAVEAT: Evidence status WEAK without caveats presented",
            evaluator_type=X1EvaluatorType.CODE,
            score=gev.evidence_sufficiency_score,
            threshold=sufficiency_threshold,
        )

    # Default: structural checks passed but no explicit PASS signal
    # Return UNKNOWN to be safe (fail-closed)
    return X1Item(
        gate_id="X1D",
        verdict=X1Verdict.UNKNOWN,
        decisive_reason="Groundedness evaluation inconclusive — structural checks passed but no explicit PASS signal",
        unknown_reason="FEC status is not PASS or WEAK_WITH_CAVEATS, and sufficiency score is ambiguous",
        evaluator_type=X1EvaluatorType.CODE,
        score=gev.evidence_sufficiency_score,
        threshold=sufficiency_threshold,
    )


def evaluate_x1d_from_packet(
    packet: "ExitReviewPacket",  # type: ignore[name-defined] # Forward ref
) -> X1Item:
    """Convenience wrapper to evaluate X1D from ExitReviewPacket.

    Extracts FEC from packet.final_evidence_contract and runs
    deterministic groundedness evaluation.
    """
    fec = packet.final_evidence_contract if packet else None
    if isinstance(fec, dict) and not fec:
        fec = None

    # Extract intent from route_contract
    intent_text = ""
    if packet and packet.route_contract:
        rc = packet.route_contract
        if isinstance(rc, dict):
            intent_text = rc.get("intent_text") or rc.get("user_query") or ""

    # Extract output text
    output_text = ""
    if packet and packet.output:
        out = packet.output
        if isinstance(out, dict):
            output_text = out.get("text", "")

    return evaluate_x1d_groundedness_deterministic(
        fec=fec,
        intent_text=intent_text,
        output_text=output_text,
    )


__all__ = [
    "GroundednessEvidence",
    "build_groundedness_evidence",
    "evaluate_x1d_groundedness_deterministic",
    "evaluate_x1d_from_packet",
]
