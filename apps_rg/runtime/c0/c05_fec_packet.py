"""C0.5 — freeze FinalEvidenceContract for PA (governed agentic_core type only)."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
)

from apps_rg.runtime.bindings.c0_binding import APPS_RG_C0_CERT_REF, _provisional_digest
from apps_rg.runtime.c0.c02_evidence_fetch import c02_atom_to_evidence_item
from apps_rg.runtime.c0.c02_hybrid_receipt_truth import normalize_c02_vector_query_receipt
from apps_rg.runtime.c0.c0_section_authority import (
    AUTHORITY_CLASS_LEDGER_GRAPH_PROOF,
    C0_AUTHORITY_MODE,
)
from apps_rg.runtime.c0.constants import FORBIDDEN_PROOF_SOURCE_TYPES


def _merge_hybrid_enrichment_items(
    items: list[EvidenceItem],
    *,
    allowed_set: set[str],
    hybrid_items: list[EvidenceItem],
    hybrid_excluded: list[str],
) -> tuple[list[EvidenceItem], int]:
    """Append product hybrid hits (non-authoritative) not already in ledger proof set."""
    seen = {getattr(i, "source_id", "") or i.source for i in items}
    count = 0
    for raw_it in hybrid_items:
        it = raw_it
        key = getattr(it, "source_id", "") or it.source
        if key in allowed_set:
            hybrid_excluded.append(f"product_hybrid_not_admitted_as_proof:{key}")
            continue
        if key not in seen:
            items.append(it)
            seen.add(key)
            count += 1
    return items, count


def _strip_forbidden_items(items: list[EvidenceItem]) -> tuple[list[EvidenceItem], list[str]]:
    kept: list[EvidenceItem] = []
    excluded: list[str] = []
    for it in items:
        st = str(getattr(it, "source_type", "") or "")
        src = str(getattr(it, "source", "") or "")
        if st in FORBIDDEN_PROOF_SOURCE_TYPES or src in ("jd_payload", "resume_payload"):
            excluded.append(f"excluded:{src or st}")
            continue
        if len(str(getattr(it, "content", "") or "")) > 800:
            excluded.append(f"excluded:paragraph_blob:{src}")
            continue
        kept.append(it)
    return kept, excluded


def build_c05_final_evidence_contract(
    *,
    section_id: str,
    atoms: list[dict[str, Any]],
    strata: dict[str, list[str]],
    graph_bindings: list[dict[str, Any]],
    front_spine: Any,
    allowed_fact_ids: list[str],
    excluded_refs: list[str] | None = None,
    retrieval_plan: dict[str, Any] | None = None,
    product_hybrid: dict[str, Any] | None = None,
) -> tuple[FinalEvidenceContract, dict[str, Any]]:
    """Build section FEC — apps_rg evidence room is default authority; hybrid via profile only."""
    del front_spine  # reserved for future bounded context; no legacy spine merge
    ts = datetime.now(timezone.utc).isoformat()
    hybrid_doc = product_hybrid or {}
    hybrid_items = list(hybrid_doc.get("enrichment_items") or [])
    allowed_set = set(allowed_fact_ids)
    items: list[EvidenceItem] = []
    for atom in atoms:
        fid = str(atom.get("fact_id") or "")
        if fid not in allowed_set:
            continue
        item = c02_atom_to_evidence_item(atom, timestamp_iso=ts)
        items.append(
            replace(
                item,
                authority_class=AUTHORITY_CLASS_LEDGER_GRAPH_PROOF,
                source_owner_or_authority=C0_AUTHORITY_MODE,
            )
        )
    hybrid_excluded: list[str] = []
    hybrid_enrichment_count = 0
    raw_vq = dict(
        hybrid_doc.get("c02_vector_query")
        or {
            "schema_version": "c02_vector_query_v1",
            "section_id": section_id,
            "product_hybrid_required": False,
            "product_hybrid_attempted": False,
            "failure_reason": "product_hybrid_not_run",
        }
    )
    vector_query_receipt = normalize_c02_vector_query_receipt(raw_vq, section_id=section_id)
    if hybrid_items:
        items, hybrid_enrichment_count = _merge_hybrid_enrichment_items(
            items,
            allowed_set=allowed_set,
            hybrid_items=hybrid_items,
            hybrid_excluded=hybrid_excluded,
        )
    items, more_ex = _strip_forbidden_items(items)
    hybrid_excluded.extend(more_ex)
    digest = _provisional_digest(items)
    support = SUPPORT_STATUS_PASS if items else SUPPORT_STATUS_WEAK
    run_id = hashlib.sha256(f"{section_id}:{digest}".encode()).hexdigest()[:16]
    plan_ref = ""
    if retrieval_plan:
        plan_ref = f"c01_retrieval_plan:{section_id}"
    fec = FinalEvidenceContract(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        tenant_id="local",
        l5_certification_ref=APPS_RG_C0_CERT_REF,
        evidence_items=tuple(items),
        support_target_met=bool(
            [
                i
                for i in items
                if getattr(i, "authority_class", "") == AUTHORITY_CLASS_LEDGER_GRAPH_PROOF
            ]
        ),
        support_status=support,
        evidence_strata=tuple(
            (k, tuple(v)) for k, v in (strata if isinstance(strata, dict) else {}).items()
        ),
        excluded_evidence_refs=tuple((excluded_refs or []) + hybrid_excluded),
        final_evidence_digest=digest,
        evidence_collection_timestamp=ts,
        graph_expansion_refs=tuple(
            f"graph:{b.get('fact_id')}" for b in graph_bindings if b.get("claim_support_allowed")
        ),
        retrieval_plan_ref=plan_ref,
    )
    receipt = {
        "schema_version": "c05_fec_packet_v1",
        "section_id": section_id,
        "allowed_fact_ids": list(allowed_fact_ids),
        "evidence_item_count": len(items),
        "ledger_proof_item_count": sum(
            1
            for i in items
            if getattr(i, "authority_class", "") == AUTHORITY_CLASS_LEDGER_GRAPH_PROOF
        ),
        "product_hybrid_enrichment_item_count": hybrid_enrichment_count,
        "product_hybrid_required": bool(hybrid_doc.get("required")),
        "graph_binding_count": len(graph_bindings),
        "final_evidence_digest": digest,
        "support_status": support,
        "c0_authority_mode": C0_AUTHORITY_MODE,
        "hybrid_excluded": hybrid_excluded,
        "c02_vector_query": vector_query_receipt,
        "data_only": True,
        "section_fec_authority": "apps_rg_c0_evidence_room",
    }
    return fec, receipt


__all__ = ["build_c05_final_evidence_contract"]
