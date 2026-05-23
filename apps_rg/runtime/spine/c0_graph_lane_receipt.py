"""C0.3 graph lane receipt — documents NA deferral vs skills-graph binding (W5).

Core Graph RAG (REQ C0.3) remains deferred per ``C0_graph_lane_deferral.md``.
This receipt is the product-visible proof surface for graph_lane_ref on section paths.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF

C0_GRAPH_LANE_RECEIPT_ARTIFACT = "c0_graph_lane_receipt.json"
DEFERRAL_SSOT = "apps_rg/config/domain_contract/C0_graph_lane_deferral.md"


def build_c0_graph_lane_receipt(
    *,
    section_id: str,
    graph_lane_ref: str,
    graph_expansion_refs: tuple[str, ...] | list[str] | None = None,
    skills_graph_bound: bool = False,
    c03_graphrag_bound_status: str = "",
) -> dict[str, Any]:
    """Build graph-lane classification receipt (not a claim of full C0.3 Graph RAG)."""
    refs = list(graph_expansion_refs or ())
    if not refs and graph_lane_ref:
        refs = [graph_lane_ref]
    deferred = graph_lane_ref == C0_GRAPH_LANE_NA_REF or not graph_lane_ref
    return {
        "schema_version": "apps_rg_c0_graph_lane_receipt_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "section_id": section_id,
        "graph_lane_ref": graph_lane_ref or C0_GRAPH_LANE_NA_REF,
        "graph_expansion_refs": refs,
        "graph_lane_deferred": deferred,
        "canonical_c0_3_graph_rag_claimed": False,
        "skills_graph_bound": skills_graph_bound,
        "c03_graphrag_bound_status": c03_graphrag_bound_status,
        "deferral_ssot": DEFERRAL_SSOT,
        "explicit_non_claims": [
            "NOT full core C0.3 Graph RAG — see C0_graph_lane_deferral.md",
            "skills_graph_bound is apps_rg proof-pool metadata, not core graphrag lane",
        ],
    }


def build_c0_graph_lane_receipt_from_spine_retrieve(
    receipt: dict[str, Any],
    *,
    section_id: str = "",
) -> dict[str, Any]:
    return build_c0_graph_lane_receipt(
        section_id=section_id or str(receipt.get("section_id") or ""),
        graph_lane_ref=str(receipt.get("graph_lane_na_ref") or C0_GRAPH_LANE_NA_REF),
        graph_expansion_refs=receipt.get("graph_expansion_refs") or (),
        skills_graph_bound=not bool(receipt.get("graph_lane_deferred")),
    )


def build_c0_graph_lane_receipt_from_bridge(
    bridge_doc: dict[str, Any],
    *,
    section_id: str = "",
) -> dict[str, Any]:
    pp = bridge_doc.get("pa_proof_authority_metadata") or bridge_doc.get("proof_pool_metadata") or {}
    if not isinstance(pp, dict):
        pp = {}
    c03 = pp.get("c03_graphrag_bound") if isinstance(pp.get("c03_graphrag_bound"), dict) else {}
    status = str(c03.get("support_status") or pp.get("c03_graphrag_bound_status") or "")
    graph_ref = str(bridge_doc.get("graph_lane_na_ref") or C0_GRAPH_LANE_NA_REF)
    refs = bridge_doc.get("graph_expansion_refs") or c03.get("graph_lineage_refs") or ()
    skills = bool(c03.get("graph_lineage_refs")) or status == "SUPPORTED"
    return build_c0_graph_lane_receipt(
        section_id=section_id or str(bridge_doc.get("section_id") or ""),
        graph_lane_ref=graph_ref,
        graph_expansion_refs=refs if isinstance(refs, (list, tuple)) else (refs,),
        skills_graph_bound=skills,
        c03_graphrag_bound_status=status,
    )


def emit_c0_graph_lane_receipt(
    artifact_dir: Path | str,
    receipt: dict[str, Any],
) -> Path:
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / C0_GRAPH_LANE_RECEIPT_ARTIFACT
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


__all__ = [
    "C0_GRAPH_LANE_RECEIPT_ARTIFACT",
    "DEFERRAL_SSOT",
    "build_c0_graph_lane_receipt",
    "build_c0_graph_lane_receipt_from_bridge",
    "build_c0_graph_lane_receipt_from_spine_retrieve",
    "emit_c0_graph_lane_receipt",
]
