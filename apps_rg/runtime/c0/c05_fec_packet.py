"""C0.5 — freeze FinalEvidenceContract for PA (governed agentic_core type)."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
    EvidenceItem,
)

from apps_rg.runtime.bindings.c0_binding import (
    APPS_RG_C0_CERT_REF,
    c0_retrieve_apps_rg,
    _provisional_digest,
)
from apps_rg.runtime.c0.c02_evidence_fetch import c02_atom_to_evidence_item
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


def build_c05_final_evidence_contract(
    *,
    section_id: str,
    atoms: list[dict[str, Any]],
    strata: dict[str, list[str]],
    graph_bindings: list[dict[str, Any]],
    front_spine: Any,
    allowed_fact_ids: list[str],
    excluded_refs: list[str] | None = None,
    merge_canonical_c0: bool = True,
) -> tuple[FinalEvidenceContract, dict[str, Any]]:
    """Build governed FEC; optionally merge spine c0_retrieve (JD stripped)."""
    ts = datetime.now(timezone.utc).isoformat()
    allowed_set = set(allowed_fact_ids)
    items: list[EvidenceItem] = []
    for atom in atoms:
        if str(atom.get("fact_id") or "") not in allowed_set:
            continue
        items.append(c02_atom_to_evidence_item(atom, timestamp_iso=ts))
    spine_excluded: list[str] = []
    if merge_canonical_c0 and front_spine is not None:
        route = getattr(front_spine, "route", None)
        vr = getattr(front_spine, "validated_request", None)
        if route is not None and vr is not None:
            chroma = os.environ.get("CHROMA_PERSIST_DIR", "").strip() or None
            try:
                spine_fec = c0_retrieve_apps_rg(
                    route,
                    vr,
                    chromadb_path=chroma,
                    timestamp_iso=ts,
                )
                spine_items, spine_excluded = _strip_forbidden_items(list(spine_fec.evidence_items))
                seen = {getattr(i, "source_id", "") or i.source for i in items}
                for it in spine_items:
                    key = getattr(it, "source_id", "") or it.source
                    if key not in seen:
                        items.append(it)
                        seen.add(key)
            except Exception:
                spine_excluded.append("spine_c0_retrieve_skipped:bounded_section_path")
    items, more_ex = _strip_forbidden_items(items)
    spine_excluded.extend(more_ex)
    digest = _provisional_digest(items)
    support = SUPPORT_STATUS_PASS if items else SUPPORT_STATUS_WEAK
    run_id = hashlib.sha256(f"{section_id}:{digest}".encode()).hexdigest()[:16]
    fec = FinalEvidenceContract(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        tenant_id="local",
        l5_certification_ref=APPS_RG_C0_CERT_REF,
        evidence_items=tuple(items),
        support_target_met=bool(items),
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
    )
    receipt = {
        "schema_version": "c05_fec_packet_v1",
        "section_id": section_id,
        "allowed_fact_ids": list(allowed_fact_ids),
        "evidence_item_count": len(items),
        "graph_binding_count": len(graph_bindings),
        "final_evidence_digest": digest,
        "support_status": support,
        "agentic_core_binding": "apps_rg.runtime.bindings.c0_binding.c0_retrieve_apps_rg",
        "data_only": True,
    }
    return fec, receipt


__all__ = ["build_c05_final_evidence_contract"]
