"""Positive truth fields for C0.2 product hybrid receipts (no spine-enrich vocabulary)."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.bindings.c0_binding import SectionRetrievalProfile

C02_VECTOR_QUERY_SCHEMA = "c02_vector_query_v1"
RETRIEVAL_PROFILE_SSOT = "apps_rg/config/domain_contract/section_retrieval_profile.yaml"
FORBIDDEN_RECEIPT_REASON = "spine_chroma_enrich_disabled"


def retrieval_profile_ref(section_id: str) -> str:
    profile = SectionRetrievalProfile()
    row = profile.get_section_config(section_id)
    if row:
        rid = str(row.get("retrieval_profile_id") or "").strip()
        if rid:
            return rid
    return f"{RETRIEVAL_PROFILE_SSOT}#{section_id}"


def bm25_available_from_sparse_refs(sparse_refs: list[str], *, sparse_lane: str) -> bool:
    if not sparse_refs:
        return sparse_lane == "not_run"
    if any("UNAVAILABLE" in ref for ref in sparse_refs):
        return False
    return sparse_lane in ("completed", "not_run")


def failure_reason_for_hybrid_miss(
    *,
    product_hybrid_required: bool,
    product_hybrid_attempted: bool,
    lanes: dict[str, str],
    sparse_refs: list[str],
    base_reason: str = "",
) -> str:
    if base_reason and base_reason != FORBIDDEN_RECEIPT_REASON:
        return base_reason
    if not product_hybrid_required:
        return "product_hybrid_not_required"
    if product_hybrid_attempted:
        if lanes.get("sparse") == "failed_BLOCKED" or any(
            "UNAVAILABLE" in ref for ref in sparse_refs
        ):
            return "product_hybrid_sparse_bm25_unavailable"
        if lanes.get("dense") != "completed":
            return "product_hybrid_dense_lane_incomplete"
        return ""
    return "product_hybrid_not_attempted"


def build_product_hybrid_truth_receipt(
    *,
    section_id: str,
    product_hybrid_required: bool,
    product_hybrid_attempted: bool,
    dense_attempted: bool,
    sparse_attempted: bool,
    bm25_available: bool,
    failure_reason: str = "",
    proof_classification: str | None = None,
    lanes: dict[str, str] | None = None,
    retrieval_mode: str = "",
    hybrid_enrichment_item_count: int = 0,
    dense_search_refs: list[str] | None = None,
    sparse_search_refs: list[str] | None = None,
    status: str = "",
) -> dict[str, Any]:
    """Canonical positive receipt block for ``c02_vector_query`` and C0 room bundles."""
    from apps_rg.runtime.c02_chroma_lifecycle import resolve_proof_class

    lane_map = dict(lanes or {})
    reason = (failure_reason or "").strip()
    if reason == FORBIDDEN_RECEIPT_REASON:
        reason = failure_reason_for_hybrid_miss(
            product_hybrid_required=product_hybrid_required,
            product_hybrid_attempted=product_hybrid_attempted,
            lanes=lane_map,
            sparse_refs=list(sparse_search_refs or []),
        )
    receipt: dict[str, Any] = {
        "schema_version": C02_VECTOR_QUERY_SCHEMA,
        "section_id": section_id,
        "retrieval_profile_ref": retrieval_profile_ref(section_id),
        "product_hybrid_required": product_hybrid_required,
        "product_hybrid_attempted": product_hybrid_attempted,
        "dense_attempted": dense_attempted,
        "sparse_attempted": sparse_attempted,
        "bm25_available": bm25_available,
        "failure_reason": reason,
        "proof_classification": proof_classification or resolve_proof_class(),
        "product_hybrid": product_hybrid_required or product_hybrid_attempted,
        "attempted": product_hybrid_attempted,
        "lanes": lane_map,
        "c0_authority_mode": "ledger_graph_primary",
        "hybrid_enrichment_item_count": hybrid_enrichment_item_count,
    }
    if retrieval_mode:
        receipt["c0_retrieval_mode"] = retrieval_mode
    if reason:
        receipt["reason"] = reason
    if status:
        receipt["status"] = status
    if dense_search_refs:
        receipt["dense_search_refs"] = dense_search_refs
    if sparse_search_refs:
        receipt["sparse_search_refs"] = sparse_search_refs
    return receipt


def normalize_c02_vector_query_receipt(raw: dict[str, Any], *, section_id: str) -> dict[str, Any]:
    """Ensure legacy or partial receipts expose positive truth fields."""
    vq = dict(raw)
    lanes = dict(vq.get("lanes") or {})
    sparse_refs = list(vq.get("sparse_search_refs") or [])
    hybrid_required = bool(
        vq.get("product_hybrid_required", vq.get("product_hybrid"))
    )
    hybrid_attempted = bool(vq.get("product_hybrid_attempted", vq.get("attempted")))
    dense_attempted = bool(vq.get("dense_attempted"))
    if not dense_attempted:
        dense_attempted = lanes.get("dense") in ("completed", "required") or bool(
            vq.get("dense_search_refs")
        )
    sparse_attempted = bool(vq.get("sparse_attempted"))
    if not sparse_attempted:
        sparse_attempted = lanes.get("sparse") in (
            "completed",
            "failed_BLOCKED",
            "required",
        ) or bool(sparse_refs)
    bm25 = vq.get("bm25_available")
    if bm25 is None:
        bm25 = bm25_available_from_sparse_refs(
            sparse_refs, sparse_lane=str(lanes.get("sparse") or "not_run")
        )
    base_reason = str(vq.get("failure_reason") or vq.get("reason") or "")
    return build_product_hybrid_truth_receipt(
        section_id=section_id,
        product_hybrid_required=hybrid_required,
        product_hybrid_attempted=hybrid_attempted,
        dense_attempted=dense_attempted,
        sparse_attempted=sparse_attempted,
        bm25_available=bool(bm25),
        failure_reason=base_reason,
        proof_classification=str(vq.get("proof_classification") or ""),
        lanes=lanes,
        retrieval_mode=str(vq.get("c0_retrieval_mode") or ""),
        hybrid_enrichment_item_count=int(vq.get("hybrid_enrichment_item_count") or 0),
        dense_search_refs=list(vq.get("dense_search_refs") or []) or None,
        sparse_search_refs=sparse_refs or None,
        status=str(vq.get("status") or ""),
    )


__all__ = [
    "FORBIDDEN_RECEIPT_REASON",
    "RETRIEVAL_PROFILE_SSOT",
    "build_product_hybrid_truth_receipt",
    "bm25_available_from_sparse_refs",
    "failure_reason_for_hybrid_miss",
    "normalize_c02_vector_query_receipt",
    "retrieval_profile_ref",
]
