"""C0.5 — freeze FinalEvidenceContract for PA (governed agentic_core type only)."""

from __future__ import annotations

import hashlib
import os
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
)

from apps_rg.runtime.bindings.c0_binding import (
    APPS_RG_C0_CERT_REF,
    C0EvidenceGapError,
    c0_retrieve_apps_rg,
    _provisional_digest,
)
from apps_rg.runtime.c0.c02_evidence_fetch import c02_atom_to_evidence_item
from apps_rg.runtime.c0.c0_section_authority import (
    AUTHORITY_CLASS_LEDGER_GRAPH_PROOF,
    AUTHORITY_CLASS_SPINE_ENRICHMENT,
    C0_AUTHORITY_MODE,
    resolve_spine_chroma_enrich,
)
from apps_rg.runtime.c0.constants import FORBIDDEN_PROOF_SOURCE_TYPES


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


def _mark_spine_enrichment_item(item: EvidenceItem) -> EvidenceItem:
    """Spine Chroma hits are enrichment by default — not proof authority."""
    return replace(
        item,
        authority_class=AUTHORITY_CLASS_SPINE_ENRICHMENT,
        source_owner_or_authority="spine_chroma_enrich_non_authoritative",
    )


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
    merge_canonical_c0: bool | None = None,
    spine_chroma_enrich: bool | None = None,
) -> tuple[FinalEvidenceContract, dict[str, Any]]:
    """Build section FEC — apps_rg room is default authority; spine enrich is opt-in."""
    ts = datetime.now(timezone.utc).isoformat()
    enrich = resolve_spine_chroma_enrich(
        explicit=spine_chroma_enrich,
        merge_canonical_c0=merge_canonical_c0,
    )
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
    spine_excluded: list[str] = []
    spine_enrichment_count = 0
    vector_query_receipt: dict[str, Any] = {
        "schema_version": "c02_vector_query_v1",
        "attempted": False,
        "reason": "spine_chroma_enrich_disabled",
    }
    if enrich and front_spine is not None:
        route = getattr(front_spine, "route", None)
        vr = getattr(front_spine, "validated_request", None)
        if route is not None and vr is not None:
            chroma = os.environ.get("CHROMA_PERSIST_DIR", "").strip() or None
            vector_query_receipt["attempted"] = True
            vector_query_receipt["reason"] = "spine_chroma_enrich_c05"
            try:
                spine_fec = c0_retrieve_apps_rg(
                    route,
                    vr,
                    chromadb_path=chroma,
                    timestamp_iso=ts,
                )
                spine_items, spine_excluded = _strip_forbidden_items(list(spine_fec.evidence_items))
                seen = {getattr(i, "source_id", "") or i.source for i in items}
                for raw_it in spine_items:
                    it = _mark_spine_enrichment_item(raw_it)
                    key = getattr(it, "source_id", "") or it.source
                    if key in allowed_set:
                        spine_excluded.append(f"spine_not_admitted_as_proof:{key}")
                        continue
                    if key not in seen:
                        items.append(it)
                        seen.add(key)
                        spine_enrichment_count += 1
                vector_query_receipt["spine_item_count"] = spine_enrichment_count
                vector_query_receipt["status"] = "PASS"
            except C0EvidenceGapError:
                raise
            except Exception as exc:
                from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

                vector_query_receipt["status"] = "FAIL"
                vector_query_receipt["error"] = str(exc)
                if product_fail_closed_runtime():
                    raise C0EvidenceGapError(
                        f"spine_chroma_enrich failed on section path: {exc}"
                    ) from exc
                spine_excluded.append("spine_chroma_enrich_skipped:section_path")
    items, more_ex = _strip_forbidden_items(items)
    spine_excluded.extend(more_ex)
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
        support_target_met=bool([i for i in items if getattr(i, "authority_class", "") == AUTHORITY_CLASS_LEDGER_GRAPH_PROOF]),
        support_status=support,
        evidence_strata=tuple(
            (k, tuple(v)) for k, v in (strata if isinstance(strata, dict) else {}).items()
        ),
        excluded_evidence_refs=tuple((excluded_refs or []) + spine_excluded),
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
            1 for i in items if getattr(i, "authority_class", "") == AUTHORITY_CLASS_LEDGER_GRAPH_PROOF
        ),
        "spine_enrichment_item_count": spine_enrichment_count,
        "graph_binding_count": len(graph_bindings),
        "final_evidence_digest": digest,
        "support_status": support,
        "c0_authority_mode": C0_AUTHORITY_MODE,
        "spine_chroma_enrich": enrich,
        "merge_canonical_c0": enrich,
        "spine_excluded": spine_excluded,
        "c02_vector_query": vector_query_receipt,
        "data_only": True,
        "section_fec_authority": "apps_rg_c0_evidence_room",
    }
    return fec, receipt


__all__ = ["build_c05_final_evidence_contract"]
