"""C0.2 Chroma write vs query lifecycle policy (ingest ≠ retrieval).



Product section runs consume governed indexes; they must not depend on same-run

``fact_vectors`` upsert for product PASS evidence.

"""



from __future__ import annotations



import json

import os

from pathlib import Path

from typing import Any



from apps_rg.runtime.c0.c02_hybrid_receipt_truth import (

    FORBIDDEN_RECEIPT_REASON,

    build_product_hybrid_truth_receipt,

    bm25_available_from_sparse_refs,

    failure_reason_for_hybrid_miss,

    normalize_c02_vector_query_receipt,

)

INDEX_BUILD_RECEIPT_NAME = "index_build_receipt.json"

C02_CHROMA_WRITE_SKIPPED = "skipped_not_required"

C02_CHROMA_WRITE_ATTEMPTED = "ATTEMPTED"

PROOF_CLASS_INDEX_MAINTENANCE = "INDEX_MAINTENANCE"

PROOF_CLASS_SHORTCUTS_ALLOWED = "SHORTCUTS_ALLOWED"

C0_AUTHORITY_LEDGER_GRAPH_PRIMARY = "ledger_graph_primary"





def _env_on(name: str) -> bool:

    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")





def c02_index_refresh_allowed() -> bool:

    """Explicit operator/CI index maintenance — not product-classified."""

    return _env_on("APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH")





def product_section_skip_lane_upsert() -> bool:

    """Skip same-run lane upsert on product paths (default)."""

    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime



    if not product_fail_closed_runtime():

        return False

    if c02_index_refresh_allowed() and _env_on("APPS_RG_INDEX_MAINTENANCE_ENTRYPOINT"):

        return False

    return True





def resolve_proof_class() -> str:

    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime



    if not product_fail_closed_runtime():

        if _env_on("APPS_RG_ALLOW_PRODUCT_SHORTCUTS"):

            return PROOF_CLASS_SHORTCUTS_ALLOWED

        return "DEV_RELAXED"

    if c02_index_refresh_allowed():

        return PROOF_CLASS_INDEX_MAINTENANCE

    return "PRODUCT_STRICT"





def build_c02_chroma_write_receipt(ingest: dict[str, Any] | None) -> dict[str, Any]:

    """Normalize ingest outcome into ``c02_chroma_write`` receipt block."""

    if product_section_skip_lane_upsert():

        return {

            "schema_version": "c02_chroma_write_v1",

            "status": C02_CHROMA_WRITE_SKIPPED,

            "attempted": False,

            "upserted_count": 0,

            "bge_embed_for_write": False,

            "product_eligible": False,

            "reason": "product_section_default_no_same_run_write",

        }

    ing = ingest or {}

    attempted = bool(ing.get("attempted"))

    status = str(ing.get("status") or "NOT_APPLICABLE")

    if attempted:

        write_status = C02_CHROMA_WRITE_ATTEMPTED

    else:

        write_status = status

    return {

        "schema_version": "c02_chroma_write_v1",

        "status": write_status,

        "attempted": attempted,

        "upserted_count": int(ing.get("upserted_count") or 0),

        "bge_embed_for_write": attempted and status == "PASS",

        "product_eligible": False,

        "reason": str(ing.get("reason") or ""),

        "ingest_receipt_status": status,

    }





def build_c02_chroma_query_receipt(

    *,

    section_id: str,

    c05_receipt: dict[str, Any] | None = None,

    c0_metrics_path: Path | None = None,

) -> dict[str, Any]:

    """Summarize hybrid query lane completion with positive truth fields."""
    from apps_rg.runtime.c0.c02_product_hybrid_retrieval import (
        product_hybrid_retrieval_required,
    )

    c05 = c05_receipt or {}

    vq = dict(c05.get("c02_vector_query") or {})

    if "product_hybrid_required" in vq:
        return normalize_c02_vector_query_receipt(vq, section_id=section_id)

    hybrid_required = product_hybrid_retrieval_required(section_id)

    hybrid_attempted = bool(vq.get("product_hybrid_attempted", vq.get("attempted")))



    lanes: dict[str, str] = {"dense": "not_run", "sparse": "not_run", "metadata": "not_run"}

    retrieval_mode = "ledger_graph_primary_only"

    sparse_refs: list[str] = list(vq.get("sparse_search_refs") or [])

    dense_refs: list[str] = list(vq.get("dense_search_refs") or [])



    if hybrid_attempted and vq.get("lanes"):

        return normalize_c02_vector_query_receipt(vq, section_id=section_id)



    metrics: dict[str, Any] = {}

    if c0_metrics_path and c0_metrics_path.is_file():

        try:

            metrics = json.loads(c0_metrics_path.read_text(encoding="utf-8"))

        except (json.JSONDecodeError, OSError):

            metrics = {}

    dense_ref = str(metrics.get("dense_search_refs") or metrics.get("query_vec_ref") or "")

    if dense_ref and not dense_refs:

        dense_refs = list(metrics.get("dense_search_refs") or [dense_ref])

    sparse_refs = list(metrics.get("sparse_search_refs") or sparse_refs)

    if dense_ref or metrics.get("chroma_dense_lane_completed"):

        lanes["dense"] = "completed"

    if sparse_refs and not any("UNAVAILABLE" in str(r) for r in sparse_refs):

        lanes["sparse"] = "completed"

    elif sparse_refs:

        lanes["sparse"] = "failed_BLOCKED"

    meta_ref = metrics.get("metadata_filter_refs") or metrics.get("metadata_filter_ref")

    if meta_ref:

        lanes["metadata"] = "completed"



    if hybrid_required:

        for lane in ("dense", "sparse", "metadata"):

            if lanes.get(lane) != "completed":

                lanes[lane] = "required"



    completed = [k for k, v in lanes.items() if v == "completed"]

    if completed and len(completed) >= 2:

        retrieval_mode = "ledger_plus_hybrid_retrieval"

    elif completed == ["dense"]:

        retrieval_mode = "ledger_plus_dense_only_profile"

    elif completed == ["sparse"]:

        retrieval_mode = "ledger_plus_sparse_only_profile"

    elif completed == ["metadata"]:

        retrieval_mode = "ledger_plus_metadata_only_profile"

    elif hybrid_required:

        retrieval_mode = "C0_RETRIEVAL_LANE_SKIPPED"



    dense_attempted = lanes.get("dense") in ("completed", "required") or bool(dense_refs)

    sparse_attempted = lanes.get("sparse") in ("completed", "failed_BLOCKED", "required")

    bm25_ok = bm25_available_from_sparse_refs(

        sparse_refs, sparse_lane=str(lanes.get("sparse") or "not_run")

    )

    base_reason = str(vq.get("failure_reason") or vq.get("reason") or "")

    if base_reason == FORBIDDEN_RECEIPT_REASON:

        base_reason = ""

    fail_reason = failure_reason_for_hybrid_miss(

        product_hybrid_required=hybrid_required,

        product_hybrid_attempted=hybrid_attempted,

        lanes=lanes,

        sparse_refs=sparse_refs,

        base_reason=base_reason,

    )



    return build_product_hybrid_truth_receipt(

        section_id=section_id,

        product_hybrid_required=hybrid_required,

        product_hybrid_attempted=hybrid_attempted,

        dense_attempted=dense_attempted,

        sparse_attempted=sparse_attempted,

        bm25_available=bm25_ok,

        failure_reason=fail_reason,

        lanes=lanes,

        retrieval_mode=retrieval_mode,

        hybrid_enrichment_item_count=int(c05.get("product_hybrid_enrichment_item_count") or 0),

        dense_search_refs=dense_refs or None,

        sparse_search_refs=sparse_refs or None,

        status=str(vq.get("status") or ""),

    )





def same_run_write_blocks_product_pass(write_receipt: dict[str, Any] | None) -> bool:

    """True when same-run write must not count toward product PASS."""

    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime



    if not product_fail_closed_runtime():

        return False

    wr = write_receipt or {}

    return str(wr.get("status") or "") == C02_CHROMA_WRITE_ATTEMPTED





def index_build_receipt_bound(artifact_dir: Path | None) -> bool:

    if artifact_dir is None:

        return False

    p = artifact_dir / INDEX_BUILD_RECEIPT_NAME

    return p.is_file()





__all__ = [

    "C02_CHROMA_WRITE_ATTEMPTED",

    "C02_CHROMA_WRITE_SKIPPED",

    "C0_AUTHORITY_LEDGER_GRAPH_PRIMARY",

    "INDEX_BUILD_RECEIPT_NAME",

    "PROOF_CLASS_INDEX_MAINTENANCE",

    "build_c02_chroma_query_receipt",

    "build_c02_chroma_write_receipt",

    "c02_index_refresh_allowed",

    "index_build_receipt_bound",

    "product_section_skip_lane_upsert",

    "resolve_proof_class",

    "same_run_write_blocks_product_pass",

]

