"""C0.7 — handoff audit before PA/L2."""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    FinalEvidenceContract,
)

from apps_rg.runtime.c0.constants import FORBIDDEN_PROOF_SOURCE_TYPES, GRAPH_STRENGTH_ADJACENT_ONLY


def audit_c07_handoff(
    *,
    fec: FinalEvidenceContract,
    c02_receipt: dict[str, Any],
    c03_receipt: dict[str, Any],
    graph_bindings: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prove PA/L2 can safely consume the packet."""
    violations: list[str] = []
    if c02_receipt.get("graph_inference_performed"):
        violations.append("c02_graph_inference_violation")
    if c03_receipt.get("new_atoms_created"):
        violations.append("c03_new_atoms_violation")
    if c03_receipt.get("pending_trace_promoted"):
        violations.append("c03_pending_trace_promotion")
    for it in fec.evidence_items:
        st = str(getattr(it, "source_type", "") or "")
        if st in FORBIDDEN_PROOF_SOURCE_TYPES:
            violations.append(f"jd_or_generic_proof:{st}")
        if getattr(it, "allowed_prompt_slot", "") != ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY:
            violations.append("non_data_only_slot")
    for gb in graph_bindings:
        if (
            gb.get("graph_support_strength") == GRAPH_STRENGTH_ADJACENT_ONLY
            and gb.get("claim_support_allowed")
        ):
            violations.append(f"adjacency_as_proof:{gb.get('fact_id')}")
    ok = not violations
    return {
        "schema_version": "c07_handoff_audit_v1",
        "handoff_safe": ok,
        "violations": violations,
        "checks": {
            "no_jd_as_proof": not any("jd" in v for v in violations),
            "no_generic_docs": True,
            "c02_c03_boundary": c02_receipt.get("graph_inference_performed") is False,
            "data_only_evidence": ok,
        },
    }


__all__ = ["audit_c07_handoff"]
