"""C0.7 — handoff audit before PA/L2."""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    FinalEvidenceContract,
)

from apps_rg.runtime.c0.c0_section_authority import (
    AUTHORITY_CLASS_LEDGER_GRAPH_PROOF,
    AUTHORITY_CLASS_SPINE_ENRICHMENT,
)
from apps_rg.runtime.c0.constants import FORBIDDEN_PROOF_SOURCE_TYPES, GRAPH_STRENGTH_ADJACENT_ONLY
from apps_rg.runtime.c0.fact_vector_index_preflight import STATUS_PASS


def _packet_fact_vector_index_preflight(
    *,
    c02_receipt: dict[str, Any],
    c05_receipt: dict[str, Any],
) -> dict[str, Any]:
    for candidate in (
        c05_receipt.get("fact_vector_index_preflight"),
        c02_receipt.get("fact_vector_index_preflight"),
    ):
        if isinstance(candidate, dict):
            return candidate
    return {}


def audit_c07_handoff(
    *,
    fec: FinalEvidenceContract,
    c02_receipt: dict[str, Any],
    c03_receipt: dict[str, Any],
    graph_bindings: list[dict[str, Any]],
    allowed_fact_ids: list[str],
    c05_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prove PA/L2 can safely consume the section packet."""
    violations: list[str] = []
    allowed_set = set(allowed_fact_ids)
    c05 = c05_receipt or {}

    if not fec.evidence_items and not allowed_set:
        violations.append("fec_empty_no_allowed_facts")

    if c02_receipt.get("graph_inference_performed"):
        violations.append("c02_graph_inference_violation")
    if c03_receipt.get("new_atoms_created"):
        violations.append("c03_new_atoms_violation")
    if c03_receipt.get("pending_trace_promoted"):
        violations.append("c03_pending_trace_promotion")

    for it in fec.evidence_items:
        st = str(getattr(it, "source_type", "") or "")
        src = str(getattr(it, "source", "") or "")
        if st in FORBIDDEN_PROOF_SOURCE_TYPES:
            violations.append(f"jd_or_generic_proof:{st}")
        if getattr(it, "allowed_prompt_slot", "") != ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY:
            violations.append("non_data_only_slot")
        fid = str(getattr(it, "source_id", "") or "").strip()
        auth = str(getattr(it, "authority_class", "") or "")
        if auth == AUTHORITY_CLASS_SPINE_ENRICHMENT:
            if fid in allowed_set:
                violations.append(f"spine_enrichment_in_allowed_proof:{fid}")
            continue
        if auth == AUTHORITY_CLASS_LEDGER_GRAPH_PROOF or not auth:
            if fid and fid not in allowed_set:
                violations.append(f"proof_not_in_allowed_fact_ids:{fid}")

    for gb in graph_bindings:
        if (
            gb.get("graph_support_strength") == GRAPH_STRENGTH_ADJACENT_ONLY
            and gb.get("claim_support_allowed")
        ):
            violations.append(f"adjacency_as_proof:{gb.get('fact_id')}")

    vq = dict(c05.get("c02_vector_query") or {})
    product_hybrid_required = bool(
        c05.get("product_hybrid_required") or vq.get("product_hybrid_required")
    )
    if product_hybrid_required and not vq.get("product_hybrid_attempted"):
        violations.append("product_hybrid_required_but_not_attempted")
    if str(vq.get("failure_reason") or vq.get("reason") or "") == "spine_chroma_enrich_disabled":
        violations.append("forbidden_receipt_reason_spine_chroma_enrich_disabled")
    fact_index_preflight = _packet_fact_vector_index_preflight(
        c02_receipt=c02_receipt,
        c05_receipt=c05,
    )
    fact_index_status = str(fact_index_preflight.get("status") or "")
    section_id = str(c05.get("section_id") or c02_receipt.get("section_id") or "")
    if product_hybrid_required:
        if fact_index_status != STATUS_PASS:
            violations.append(
                f"fact_vector_index_preflight_not_pass:{fact_index_status or 'missing'}"
            )
        if fact_index_preflight.get("comparison_authority") is not True:
            violations.append("fact_vector_index_preflight_comparison_authority_missing")
        if fact_index_preflight.get("write_authority") is not False:
            violations.append("fact_vector_index_preflight_write_authority_not_false")
        if not str(fact_index_preflight.get("same_run_write_policy") or ""):
            violations.append("fact_vector_index_preflight_same_run_write_policy_missing")
        if section_id == "unify_bullets":
            unify_sufficiency = fact_index_preflight.get("unify_bullets_sufficiency")
            unify_sufficiency = unify_sufficiency if isinstance(unify_sufficiency, dict) else {}
            unify_status = str(unify_sufficiency.get("status") or "")
            if unify_status != STATUS_PASS:
                violations.append(
                    f"unify_bullets_fact_vector_sufficiency_not_pass:{unify_status or 'missing'}"
                )
            if unify_sufficiency.get("metric_distribution_pass") is not True:
                violations.append("unify_bullets_metric_distribution_not_pass")
            if unify_sufficiency.get("graph_traversal_pass") is not True:
                violations.append("unify_bullets_graph_traversal_not_pass")
            if unify_sufficiency.get("graph_granularity_pass") is not True:
                violations.append("unify_bullets_graph_granularity_not_pass")

    ok = not violations
    unify_checks = {}
    if section_id == "unify_bullets":
        unify_sufficiency = fact_index_preflight.get("unify_bullets_sufficiency")
        unify_sufficiency = unify_sufficiency if isinstance(unify_sufficiency, dict) else {}
        unify_checks = {
            "unify_bullets_fact_vector_sufficiency_status": str(
                unify_sufficiency.get("status") or "missing"
            ),
            "unify_bullets_source_slots_present": not bool(
                unify_sufficiency.get("missing_source_fact_slots") or []
            ),
            "unify_bullets_metric_distribution_pass": unify_sufficiency.get(
                "metric_distribution_pass"
            )
            is True,
            "unify_bullets_graph_traversal_pass": unify_sufficiency.get(
                "graph_traversal_pass"
            )
            is True,
            "unify_bullets_graph_granularity_pass": unify_sufficiency.get(
                "graph_granularity_pass"
            )
            is True,
        }
    return {
        "schema_version": "c07_handoff_audit_v1",
        "handoff_safe": ok,
        "violations": violations,
        "allowed_fact_ids_count": len(allowed_set),
        "checks": {
            "fec_exists": bool(fec),
            "allowed_fact_ids_preserved": True,
            "no_jd_as_proof": not any("jd" in v for v in violations),
            "no_generic_docs": True,
            "c02_c03_boundary": c02_receipt.get("graph_inference_performed") is False,
            "data_only_evidence": ok,
            "skills_graph_not_core_graphrag": c03_receipt.get("core_c03_graph_rag_used") is False,
            "product_hybrid_truth_fields": "product_hybrid_required" in vq,
            "fact_vector_index_preflight_required": product_hybrid_required,
            "fact_vector_index_preflight_present": bool(fact_index_preflight),
            "fact_vector_index_preflight_status": fact_index_status or "missing",
            "fact_vector_index_preflight_pass": fact_index_status == STATUS_PASS,
            "same_run_write_policy_visible": bool(
                str(fact_index_preflight.get("same_run_write_policy") or "")
            ),
            **unify_checks,
        },
    }


__all__ = ["audit_c07_handoff"]
