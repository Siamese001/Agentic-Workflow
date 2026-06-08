"""W4.3 — product hybrid C0.2 read (dense+sparse+metadata) for section evidence room."""

from __future__ import annotations

import hashlib
import os
from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import EvidenceItem

from apps_rg.runtime.c0.c02_hybrid_receipt_truth import (
    build_product_hybrid_truth_receipt,
    bm25_available_from_sparse_refs,
    failure_reason_for_hybrid_miss,
)
from apps_rg.runtime.c0.c0_section_authority import AUTHORITY_CLASS_SPINE_ENRICHMENT

PRODUCT_HYBRID_REASON = "product_hybrid_bounded_section_retrieval"
NOT_REQUIRED_REASON = "product_hybrid_not_required"

# G5 (plan apps-rg-e2e-gap-remediation-7e2d9c): every C0.2 hard block must tell the
# operator how to recover, not just that proof is absent. doctor diagnoses prerequisites;
# bootstrap (W3) rebuilds the fact_vectors collection from tracked graph/proof-pool sources.
_C0_REMEDIATION_HINT = (
    "Remediation: run `python -m apps_rg doctor --strict` to diagnose prerequisites "
    "(.env keys, fact_vectors presence, embedding model/dim), then "
    "`python -m apps_rg bootstrap fact-vectors --strict` to (re)build the fact_vectors "
    "collection. Plan: apps-rg-e2e-gap-remediation-7e2d9c (G5/G6/G7)."
)


def product_hybrid_retrieval_required(section_id: str) -> bool:
    """True when this section lane must run bounded hybrid read (fail-closed on product)."""
    from apps_rg.runtime.c0_mandatory_policy import apps_rg_c0_dense_sparse_mandatory
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    if not product_fail_closed_runtime() or not apps_rg_c0_dense_sparse_mandatory():
        return False
    from apps_rg.runtime.bindings.c0_binding import SectionRetrievalProfile

    profile = SectionRetrievalProfile()
    if not profile.enabled:
        return False
    return profile.get_section_config(section_id) is not None


def normalize_section_app_payload(app_payload: dict[str, Any]) -> dict[str, Any]:
    """Map flat CLI ``jd_text`` into ``jd_payload.*`` paths used by retrieval profile."""
    out = dict(app_payload)
    jd_text = str(
        out.get("jd_text") or out.get("job_description_text") or ""
    ).strip()
    jd_payload = dict(out.get("jd_payload") or {})
    if jd_text and not str(jd_payload.get("jd_text") or "").strip():
        jd_payload["jd_text"] = jd_text
    tc = str(out.get("target_company") or "").strip()
    if tc and not jd_payload.get("target_company"):
        jd_payload["target_company"] = tc
    tr = str(out.get("target_role") or out.get("target_title") or "").strip()
    if tr and not jd_payload.get("target_role"):
        jd_payload["target_role"] = tr
    if jd_payload:
        out["jd_payload"] = jd_payload
    return out


def _mark_hybrid_enrichment_item(item: EvidenceItem) -> EvidenceItem:
    from dataclasses import replace

    return replace(
        item,
        authority_class=AUTHORITY_CLASS_SPINE_ENRICHMENT,
        source_owner_or_authority="product_hybrid_retrieval_non_authoritative",
    )


def _lane_status_from_refs(
    *,
    dense_completed: bool,
    sparse_refs: list[str],
    metadata_completed: bool,
) -> dict[str, str]:
    sparse_lane = "not_run"
    if sparse_refs:
        if any("UNAVAILABLE" in ref for ref in sparse_refs):
            sparse_lane = "failed_BLOCKED"
        elif any("NOT_APPLICABLE" in ref for ref in sparse_refs):
            sparse_lane = "not_run"
        else:
            sparse_lane = "completed"
    return {
        "dense": "completed" if dense_completed else "not_run",
        "sparse": sparse_lane,
        "metadata": "completed" if metadata_completed else "not_run",
    }


def _retrieval_mode_from_lanes(lanes: dict[str, str]) -> str:
    completed = [k for k, v in lanes.items() if v == "completed"]
    if len(completed) >= 2:
        return "ledger_plus_hybrid_retrieval"
    if completed == ["dense"]:
        return "ledger_plus_dense_only_profile"
    if completed == ["sparse"]:
        return "ledger_plus_sparse_only_profile"
    if completed == ["metadata"]:
        return "ledger_plus_metadata_exact_only_profile"
    return "C0_RETRIEVAL_LANE_SKIPPED"


def _enforce_mandatory_lanes(
    *,
    section_id: str,
    lanes: dict[str, str],
    sparse_refs: list[str],
) -> None:
    from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError, SectionRetrievalProfile
    from apps_rg.runtime.c0_mandatory_policy import apps_rg_c0_dense_sparse_mandatory
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    if not product_fail_closed_runtime() or not apps_rg_c0_dense_sparse_mandatory():
        return
    profile = SectionRetrievalProfile()
    section_cfg = profile.get_section_config(section_id)
    if section_cfg is None:
        return
    if lanes.get("dense") != "completed":
        raise C0EvidenceGapError(
            f"C0.2 product hybrid dense lane required for {section_id!r} but did not complete "
            f"(lane_status={lanes}). Likely cause: fact_vectors collection empty/under-populated "
            f"for this section, the section metadata filter removed all candidates, or an "
            f"embedding-function/dimension mismatch. " + _C0_REMEDIATION_HINT
        )
    sparse_cfg = profile.section_sparse_config(section_cfg)
    if sparse_cfg.get("sparse_enabled"):
        if any("UNAVAILABLE" in ref for ref in sparse_refs):
            raise C0EvidenceGapError(
                f"C0.2 product hybrid sparse lane required for {section_id!r} but BM25 unavailable: "
                + ",".join(sparse_refs[:3])
            )
        if lanes.get("sparse") != "completed":
            raise C0EvidenceGapError(
                f"C0.2 product hybrid sparse lane required for {section_id!r} but did not complete "
                f"(lane_status={lanes}). Likely cause: BM25/sparse index missing or empty for this "
                f"section. " + _C0_REMEDIATION_HINT
            )


def perform_product_hybrid_retrieval(
    *,
    section_id: str,
    app_payload: dict[str, Any],
    evidence_digest: str,
    timestamp_iso: str,
    chromadb_path: str | None = None,
) -> dict[str, Any]:
    """Run bounded hybrid read for one section; return enrichment items + vector query receipt."""
    hybrid_required = product_hybrid_retrieval_required(section_id)
    if not hybrid_required:
        lanes = {"dense": "not_run", "sparse": "not_run", "metadata": "not_run"}
        return {
            "required": False,
            "enrichment_items": [],
            "c02_vector_query": build_product_hybrid_truth_receipt(
                section_id=section_id,
                product_hybrid_required=False,
                product_hybrid_attempted=False,
                dense_attempted=False,
                sparse_attempted=False,
                bm25_available=True,
                failure_reason=NOT_REQUIRED_REASON,
                lanes=lanes,
                retrieval_mode="ledger_graph_primary_only",
            ),
            "c0_metrics_patch": {},
        }

    from apps_rg.runtime.bindings.c0_binding import (
        C0_METADATA_FILTER_REF,
        C0EvidenceGapError,
        C0_QUERY_VEC_REF_BGE,
        _perform_bounded_section_retrieval,
    )
    from apps_rg.runtime.chroma_precomputed_collection import (
        get_precomputed_embeddings_collection_for_query,
    )
    from apps_rg.runtime.embedding_settings import (
        apply_apps_rg_embedding_env_guards,
        resolve_apps_rg_embedding_settings,
    )

    chroma_path = (chromadb_path or os.environ.get("CHROMA_PERSIST_DIR", "") or "").strip()
    if not chroma_path:
        raise C0EvidenceGapError(
            f"C0.2 product hybrid mandatory for {section_id!r}: CHROMA_PERSIST_DIR required"
        )

    apply_apps_rg_embedding_env_guards(chroma_persist_dir=chroma_path)
    emb = resolve_apps_rg_embedding_settings(chroma_persist_dir=chroma_path)
    if emb.route_result == "FAIL_CLOSED":
        raise C0EvidenceGapError(emb.decisive_reason)

    payload = normalize_section_app_payload(app_payload)
    import chromadb

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        fv_col = get_precomputed_embeddings_collection_for_query(client, "fact_vectors")
    except Exception as exc:  # guardian: allow-broad-exception -- Chroma collection error taxonomy varies by version; classify as C0 evidence gap.
        raise C0EvidenceGapError(
            f"C0.2 product hybrid dense lane required for {section_id!r} but "
            f"fact_vectors collection is unavailable at {chroma_path!r}: {exc}. "
            + _C0_REMEDIATION_HINT
        ) from exc

    extra, _verdicts, status, sparse_refs, _scores, _traces = _perform_bounded_section_retrieval(
        chroma_path,
        payload,
        evidence_digest,
        timestamp_iso,
        chroma_collection=fv_col,
        section_id_filter=section_id,
    )

    dense_completed = status == "PASS" and bool(extra)
    sparse_refs_list = list(sparse_refs)
    metadata_completed = dense_completed
    lanes = _lane_status_from_refs(
        dense_completed=dense_completed,
        sparse_refs=sparse_refs_list,
        metadata_completed=metadata_completed,
    )
    _enforce_mandatory_lanes(
        section_id=section_id,
        lanes=lanes,
        sparse_refs=sparse_refs_list,
    )
    retrieval_mode = _retrieval_mode_from_lanes(lanes)
    enrichment = [_mark_hybrid_enrichment_item(it) for it in extra]

    dense_refs = [f"dense:fact_vectors:{chroma_path}"] if dense_completed else []
    bm25_ok = bm25_available_from_sparse_refs(
        sparse_refs_list, sparse_lane=str(lanes.get("sparse") or "not_run")
    )
    fail_reason = failure_reason_for_hybrid_miss(
        product_hybrid_required=True,
        product_hybrid_attempted=True,
        lanes=lanes,
        sparse_refs=sparse_refs_list,
        base_reason=PRODUCT_HYBRID_REASON if dense_completed else "product_hybrid_dense_lane_incomplete",
    )
    return {
        "required": True,
        "enrichment_items": enrichment,
        "c02_vector_query": build_product_hybrid_truth_receipt(
            section_id=section_id,
            product_hybrid_required=True,
            product_hybrid_attempted=True,
            dense_attempted=dense_completed,
            sparse_attempted=lanes.get("sparse") in ("completed", "failed_BLOCKED"),
            bm25_available=bm25_ok,
            failure_reason=fail_reason,
            lanes=lanes,
            retrieval_mode=retrieval_mode,
            hybrid_enrichment_item_count=len(enrichment),
            dense_search_refs=dense_refs,
            sparse_search_refs=sparse_refs_list,
            status=status,
        ),
        "c0_metrics_patch": {
            "dense_search_refs": dense_refs,
            "sparse_search_refs": sparse_refs_list,
            "chroma_dense_lane_completed": dense_completed,
            "query_vec_ref": C0_QUERY_VEC_REF_BGE if dense_completed else "",
            "metadata_filter_ref": C0_METADATA_FILTER_REF if metadata_completed else "",
            "metadata_filter_refs": [C0_METADATA_FILTER_REF] if metadata_completed else [],
        },
    }


def provisional_digest_from_atoms(atoms: list[dict[str, Any]]) -> str:
    parts = sorted(
        f"{a.get('fact_id')}:{hashlib.sha256(str(a.get('text_to_embed') or '').encode()).hexdigest()[:16]}"
        for a in atoms
        if a.get("fact_id")
    )
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


__all__ = [
    "normalize_section_app_payload",
    "perform_product_hybrid_retrieval",
    "product_hybrid_retrieval_required",
    "provisional_digest_from_atoms",
]
