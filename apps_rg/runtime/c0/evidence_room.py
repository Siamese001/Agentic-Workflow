"""Orchestrate apps_rg C0.1–C0.7 section evidence room."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.c0.c01_retrieval_plan import build_c01_retrieval_plan
from apps_rg.runtime.c0.c02_evidence_fetch import fetch_c02_evidence_atoms
from apps_rg.runtime.c0.c02_fact_vector_ingest import maybe_upsert_c02_fact_vectors
from apps_rg.runtime.c0.c03_graph_expansion import expand_c03_graph_bindings
from apps_rg.runtime.c0.c03_role_family import resolve_c0_role_family_key
from apps_rg.runtime.c0.c04_stratify import stratify_c04_evidence
from apps_rg.runtime.c0.c05_fec_packet import build_c05_final_evidence_contract
from apps_rg.runtime.c0.c07_handoff_audit import audit_c07_handoff
from apps_rg.runtime.c0.c0_section_authority import (
    C01_ARTIFACT,
    C02_ATOMS_ARTIFACT,
    C02_VECTOR_QUERY_ARTIFACT,
    bridge_authority_fields,
    resolve_spine_chroma_enrich,
    section_chroma_write_in_c02,
)
from apps_rg.runtime.c0.constants import C0_SECTIONS_ENABLED, REPO_ROOT
from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.section_fec_bridge import (
    FEC_BRIDGE_ARTIFACT,
    FEC_BRIDGE_MODE_SECTION,
    FEC_BRIDGE_RECEIPT,
    SectionFecBridge,
    SectionFecBridgePreconditionError,
    _build_pa_proof_authority_metadata,
    _extract_support_status,
    _utc_now,
)
from apps_rg.runtime.section_front_spine_bridge import SectionFrontSpineBridge

C0_ROOM_RECEIPT = "c0_evidence_room_receipt.json"


def section_c0_evidence_room_enabled(section_id: str) -> bool:
    if section_id not in C0_SECTIONS_ENABLED:
        return False
    import os

    return os.environ.get("APPS_RG_C0_EVIDENCE_ROOM", "1").strip() not in ("0", "false", "no")


def _write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _emit_room_artifacts(artifact_dir: Path, bundle: dict[str, Any]) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    _write_json(artifact_dir / C0_ROOM_RECEIPT, bundle)


def run_section_c0_evidence_room(
    *,
    artifact_dir: Path,
    section_id: str,
    front_spine: SectionFrontSpineBridge,
    pool: SectionProofPool,
    runtime_payload: dict[str, Any],
    role_family_key: str | None = None,
    spine_chroma_enrich: bool | None = None,
) -> SectionFecBridge:
    """Run governed C0.1–C0.7 and return FEC bridge bound to FinalEvidenceContract."""
    from apps_rg.runtime.embedding_settings import apply_apps_rg_embedding_env_guards

    apply_apps_rg_embedding_env_guards()
    ts = _utc_now()
    enrich = resolve_spine_chroma_enrich(explicit=spine_chroma_enrich)
    rf_key = role_family_key or resolve_c0_role_family_key(
        front_spine=front_spine,
        pool=pool,
        repo_root=REPO_ROOT,
    )
    target_role, jd_text, _briefing = "", "", ""
    if front_spine is not None and front_spine.validated_request is not None:
        app = getattr(front_spine.validated_request, "app_payload", None) or {}
        if isinstance(app, dict):
            target_role = str(app.get("target_role") or app.get("target_title") or "")
            jd_text = str(app.get("job_description_text") or app.get("jd_text") or "")
    if pool is not None:
        meta = pool.proof_pool_metadata or {}
        target_role = target_role or str(meta.get("target_role") or "")
        jd_text = jd_text or str(meta.get("jd_text") or "")
    plan = build_c01_retrieval_plan(
        section_id=section_id,
        route_ref="route_contract.json",
        target_role=target_role,
        role_family_key=rf_key,
        jd_text=jd_text,
    )
    _write_json(artifact_dir / C01_ARTIFACT, plan)

    c02 = fetch_c02_evidence_atoms(section_id=section_id, pool=pool, repo_root=REPO_ROOT)
    atoms = list(c02.get("atoms") or [])
    c02_atoms_doc = {k: v for k, v in c02.items() if k != "skipped"}
    c02_atoms_doc["atoms"] = atoms
    _write_json(artifact_dir / C02_ATOMS_ARTIFACT, c02_atoms_doc)

    from apps_rg.runtime.c02_chroma_lifecycle import (
        build_c02_chroma_write_receipt,
        product_section_skip_lane_upsert,
    )

    if not section_chroma_write_in_c02(enrich):
        fv_ingest: dict[str, Any] = {
            "schema_version": "c02_fact_vectors_ingest_v1",
            "section_id": section_id,
            "attempted": False,
            "upserted_count": 0,
            "skipped_count": 0,
            "status": "SKIPPED",
            "reason": "chroma_policy_defer_to_spine_enrich" if enrich else "product_section_skip_lane_upsert",
        }
    else:
        fv_ingest = maybe_upsert_c02_fact_vectors(
            atoms,
            section_id=section_id,
            artifact_dir=artifact_dir,
            repo_root=REPO_ROOT,
        )
    c02["c02_chroma_write"] = build_c02_chroma_write_receipt(fv_ingest)
    c02["fact_vectors_ingest"] = {
        k: v for k, v in fv_ingest.items() if k != "skipped"
    }
    c02["fact_vectors_ingest_skipped_count"] = fv_ingest.get("skipped_count", 0)
    c02["fact_vectors_upserted_count"] = fv_ingest.get("upserted_count", 0)

    c03 = expand_c03_graph_bindings(
        section_id=section_id,
        atoms=atoms,
        role_family_key=rf_key,
        repo_root=REPO_ROOT,
    )
    bindings = list(c03.get("bindings") or [])
    lane_proof = section_id in ("executive_summary", "headline")
    c04 = stratify_c04_evidence(
        section_id=section_id,
        atoms=atoms,
        graph_bindings=bindings,
        lane_requires_proof=lane_proof,
    )
    allowed = list(c04.get("allowed_fact_ids") or [])
    fec, c05 = build_c05_final_evidence_contract(
        section_id=section_id,
        atoms=atoms,
        strata=c04.get("strata") or {},
        graph_bindings=bindings,
        front_spine=front_spine,
        allowed_fact_ids=allowed,
        excluded_refs=list(c04.get("excluded_fact_ids") or []),
        retrieval_plan=plan,
        spine_chroma_enrich=enrich,
    )
    vector_query = dict(c05.get("c02_vector_query") or {})
    vector_query["chroma_write_in_c02"] = section_chroma_write_in_c02(enrich)
    _write_json(artifact_dir / C02_VECTOR_QUERY_ARTIFACT, vector_query)

    from apps_rg.runtime.c02_chroma_lifecycle import build_c02_chroma_query_receipt

    c02["c02_chroma_query"] = build_c02_chroma_query_receipt(
        section_id=section_id,
        c05_receipt=c05,
        c0_metrics_path=artifact_dir / "c0_metrics.json",
    )
    c07 = audit_c07_handoff(
        fec=fec,
        c02_receipt=c02,
        c03_receipt=c03,
        graph_bindings=bindings,
        allowed_fact_ids=allowed,
        c05_receipt=c05,
    )
    if not c07.get("handoff_safe"):
        raise SectionFecBridgePreconditionError(
            "C0.7 handoff audit failed — packet unsafe for section PA: "
            + ", ".join(str(v) for v in (c07.get("violations") or []))
        )
    c06 = {
        "schema_version": "c06_weak_refine_v1",
        "disabled": True,
        "reason": "receipt_only_refine_removed_use_bounded_c02_retry_when_implemented",
    }
    pp_meta = dict(pool.proof_pool_metadata or {})
    support_status = _extract_support_status(pp_meta)
    evidence_items = [
        {
            "evidence_id": f"evidence:section:{getattr(it, 'source_id', '') or it.source}",
            "source_fact_id": getattr(it, "source_id", "") or "",
            "source_class": getattr(it, "source_type", "") or pool.proof_source,
            "content_digest": getattr(it, "chunk_digest", ""),
            "allowed_prompt_slot": getattr(it, "allowed_prompt_slot", ""),
            "authority_class": getattr(it, "authority_class", ""),
        }
        for it in fec.evidence_items
    ]
    pa_meta = _build_pa_proof_authority_metadata(
        pp_meta, pool=pool, route_contract_ref="route_contract.json"
    )
    pa_meta["fec_shape_only"] = False
    pa_meta["binding_kind"] = "section_c0_evidence_room"
    pa_meta["canonical_c0_path"] = True
    authority = bridge_authority_fields(spine_chroma_enrich=enrich)
    bridge_doc: dict[str, Any] = {
        "schema_version": "section_fec_bridge_v1",
        "generated_at_utc": ts,
        "bridge_type": "FinalEvidenceContractBridge",
        "contract_type": "FinalEvidenceContract",
        "fec_bridge_mode": FEC_BRIDGE_MODE_SECTION,
        "producer_stage": "section_c0_evidence_room",
        "consumer_stage": "section_PA",
        "section_id": section_id,
        "route_contract_ref": "route_contract.json",
        "validated_request_ref": "validated_request.json",
        "l1_plan_contract_ref": "l1_plan_contract.json",
        "proof_pool_ref": pool.proof_pool_ref,
        "proof_pool_digest": pool.proof_pool_digest,
        "source_fact_ids": allowed,
        "allowed_fact_ids": allowed,
        "evidence_items": evidence_items,
        "citation_lineage_refs": [
            str(b.get("lineage_refs", [""])[0]) for b in bindings if b.get("lineage_refs")
        ],
        "graph_lineage_refs": [f"graph:{b['fact_id']}" for b in bindings],
        "graph_expansion_refs": list(fec.graph_expansion_refs or ()),
        "srfs_ref": pool.srfs_ref if pool.srfs_present else "",
        "support_status": fec.support_status or support_status,
        "canonical_c0_2_claimed": True,
        "apps_rg_c03_skills_graph_used": True,
        "core_c03_graph_rag_used": False,
        "canonical_c0_3_claimed": False,
        "canonical_c0_5_claimed": True,
        "fec_shape_only": False,
        **authority,
        "final_evidence_contract_snapshot": {
            "request_id": fec.request_id,
            "run_id": fec.run_id,
            "final_evidence_digest": fec.final_evidence_digest,
            "support_status": fec.support_status,
            "evidence_item_count": len(fec.evidence_items),
            "allowed_fact_ids": allowed,
            "excluded_evidence_refs": list(fec.excluded_evidence_refs or ()),
            "evidence_strata": dict(c04.get("strata") or {}),
            "retrieval_plan_ref": fec.retrieval_plan_ref,
        },
        "c0_evidence_room": {
            "c01": plan,
            "c01_artifact": C01_ARTIFACT,
            "c02": {k: v for k, v in c02.items() if k not in ("atoms", "skipped")},
            "c02_atoms_artifact": C02_ATOMS_ARTIFACT,
            "c02_vector_query_artifact": C02_VECTOR_QUERY_ARTIFACT,
            "c02_atom_count": len(atoms),
            "c03": {k: v for k, v in c03.items() if k != "bindings"},
            "c03_skills_graph": True,
            "c04": c04,
            "c05": c05,
            "c06": c06,
            "c07": c07,
        },
        "c07_handoff_safe": True,
        "pa_proof_authority_metadata": pa_meta,
        "product_visible": True,
    }
    bundle = {
        "bridge_doc": bridge_doc,
        "c01": plan,
        "c02": c02,
        "c03": c03,
        "c04": c04,
        "c05": c05,
        "c06": c06,
        "c07": c07,
    }
    _emit_room_artifacts(artifact_dir, bundle)
    from apps_rg.runtime.section_fec_bridge import emit_section_fec_bridge_artifacts

    bridge = SectionFecBridge(section_id=section_id, bridge_doc=bridge_doc)
    emit_section_fec_bridge_artifacts(artifact_dir, bridge)
    runtime_payload["section_fec_bridge"] = bridge_doc
    runtime_payload["fec_bridge_ref"] = FEC_BRIDGE_ARTIFACT
    runtime_payload["final_evidence_contract_ref"] = FEC_BRIDGE_ARTIFACT
    runtime_payload["c0_fec_bridge_receipt_ref"] = FEC_BRIDGE_RECEIPT
    runtime_payload["canonical_final_evidence_contract_snapshot"] = bridge_doc[
        "final_evidence_contract_snapshot"
    ]
    runtime_payload["raw_proof_pool_direct_to_pa"] = False
    runtime_payload["product_visible"] = True
    runtime_payload["c0_authority_mode"] = authority["c0_authority_mode"]
    runtime_payload["spine_chroma_enrich"] = enrich
    return bridge


__all__ = [
    "C0_ROOM_RECEIPT",
    "run_section_c0_evidence_room",
    "section_c0_evidence_room_enabled",
]
