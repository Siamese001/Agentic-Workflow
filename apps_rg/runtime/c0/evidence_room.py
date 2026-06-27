"""Orchestrate apps_rg C0.1–C0.7 section evidence room."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.c0.c0_section_authority import (
    C01_ARTIFACT,
    C02_ATOMS_ARTIFACT,
    C02_VECTOR_QUERY_ARTIFACT,
    bridge_authority_fields,
    section_chroma_write_in_c02,
)
from apps_rg.runtime.c0.c01_retrieval_plan import build_c01_retrieval_plan
from apps_rg.runtime.c0.c02_evidence_fetch import fetch_c02_evidence_atoms
from apps_rg.runtime.c0.c02_fact_vector_ingest import (
    maybe_upsert_c02_fact_vectors,
    maybe_upsert_c05_fact_vector_write_back_atoms,
)
from apps_rg.runtime.c0.c02_hybrid_receipt_truth import normalize_c02_vector_query_receipt
from apps_rg.runtime.c0.c03_graph_expansion import expand_c03_graph_bindings
from apps_rg.runtime.c0.c03_role_family import resolve_c0_role_family_key
from apps_rg.runtime.c0.c04_stratify import stratify_c04_evidence
from apps_rg.runtime.c0.c05_fec_packet import build_c05_final_evidence_contract
from apps_rg.runtime.c0.c07_handoff_audit import audit_c07_handoff
from apps_rg.runtime.c0.constants import C0_SECTIONS_ENABLED, REPO_ROOT
from apps_rg.runtime.c0 import fact_vector_index_preflight
from apps_rg.runtime.c0.product_runtime_guards import ENV_APPS_RG_C0_EVIDENCE_ROOM
from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.spine.c0_fec_compose import (
    FEC_BRIDGE_ARTIFACT,
    FEC_BRIDGE_MODE_SECTION,
    FEC_BRIDGE_RECEIPT,
    SectionFecBridge,
    SectionFecBridgePreconditionError,
    _build_pa_proof_authority_metadata,
    _extract_support_status,
    _utc_now,
)
from apps_rg.runtime.spine.front_contracts import SectionFrontSpineBridge

# Reachability anchors for the package barrels that fan out to the new hardening leaves.
from ... import fact_inventory as _fact_inventory
from ...runtime.graph import graph_metric_diversity_policy as _graph_metric_diversity_policy

_REACHABILITY_ANCHORS = (
    _fact_inventory,
    _graph_metric_diversity_policy,
)

C0_ROOM_RECEIPT = "c0_evidence_room_receipt.json"


def section_c0_evidence_room_enabled(section_id: str) -> bool:
    if section_id not in C0_SECTIONS_ENABLED:
        return False
    import os

    from apps_rg.runtime.c0.product_runtime_guards import assert_canonical_product_section_env

    env_off = os.environ.get(ENV_APPS_RG_C0_EVIDENCE_ROOM, "1").strip().lower() in (
        "0",
        "false",
        "no",
    )
    if env_off:
        assert_canonical_product_section_env(section_id)
        return False
    return True


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
) -> SectionFecBridge:
    """Run governed C0.1–C0.7 and return FEC bridge bound to FinalEvidenceContract."""
    from apps_rg.runtime.embedding_settings import apply_apps_rg_embedding_env_guards

    apply_apps_rg_embedding_env_guards()
    ts = _utc_now()
    run_id = str(runtime_payload.get("run_id") or artifact_dir.name)
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
    )

    if not section_chroma_write_in_c02():
        fv_ingest: dict[str, Any] = {
            "schema_version": "c02_fact_vectors_ingest_v1",
            "section_id": section_id,
            "attempted": False,
            "upserted_count": 0,
            "skipped_count": 0,
            "status": "SKIPPED",
            "reason": "product_section_skip_lane_upsert",
        }
    else:
        fv_ingest = maybe_upsert_c02_fact_vectors(
            atoms,
            section_id=section_id,
            artifact_dir=artifact_dir,
            repo_root=REPO_ROOT,
            run_id=run_id,
        )
    c02["c02_chroma_write"] = build_c02_chroma_write_receipt(fv_ingest)
    c02["fact_vectors_ingest"] = {
        k: v for k, v in fv_ingest.items() if k != "skipped"
    }
    c02["fact_vectors_ingest_skipped_count"] = fv_ingest.get("skipped_count", 0)
    c02["fact_vectors_upserted_count"] = fv_ingest.get("upserted_count", 0)
    fact_index_preflight = fact_vector_index_preflight.build_fact_vector_index_preflight(
        section_id=section_id,
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        role_family_key=rf_key,
    )
    c02["fact_vector_index_preflight"] = fact_index_preflight
    c02["fact_vector_index_preflight_ref"] = (
        fact_vector_index_preflight.FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT
    )

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
    if section_id == "executive_summary":
        from apps_rg.runtime.c0.c04_exec_summary_shaping import shape_executive_summary_c04

        c04 = shape_executive_summary_c04(c04, bindings=bindings, atoms=atoms)
    from apps_rg.runtime.evidence.canonical_section_evidence_set import (
        apply_canonical_section_evidence_materialization,
        build_canonical_section_evidence_set,
        canonical_evidence_set_digest,
        materialize_fec_allowed_from_c04,
    )

    canonical = build_canonical_section_evidence_set(pool)
    allowed, fec_materialization_receipt = materialize_fec_allowed_from_c04(
        c04_allowed=list(c04.get("allowed_fact_ids") or []),
        canonical=canonical,
    )
    runtime_payload["canonical_section_evidence_set"] = canonical.as_dict()
    runtime_payload["fec_materialization_receipt"] = fec_materialization_receipt
    app_payload: dict[str, Any] = {}
    if front_spine is not None and front_spine.validated_request is not None:
        app_payload = dict(getattr(front_spine.validated_request, "app_payload", None) or {})
    if not app_payload.get("jd_text") and jd_text:
        app_payload["jd_text"] = jd_text
    if not app_payload.get("target_role") and target_role:
        app_payload["target_role"] = target_role

    from apps_rg.runtime.c0.c02_product_hybrid_retrieval import (
        perform_product_hybrid_retrieval,
        provisional_digest_from_atoms,
    )

    hybrid_digest = provisional_digest_from_atoms(atoms)
    product_hybrid = perform_product_hybrid_retrieval(
        section_id=section_id,
        app_payload=app_payload,
        evidence_digest=hybrid_digest,
        timestamp_iso=ts,
    )
    metrics_patch = dict(product_hybrid.get("c0_metrics_patch") or {})
    if metrics_patch:
        metrics_path = artifact_dir / "c0_metrics.json"
        metrics_doc = {
            "schema_version": "c0_metrics.v1",
            "run_id": run_id,
            "section_id": section_id,
            **metrics_patch,
        }
        _write_json(metrics_path, metrics_doc)

    fec, c05 = build_c05_final_evidence_contract(
        section_id=section_id,
        atoms=atoms,
        strata=c04.get("strata") or {},
        graph_bindings=bindings,
        front_spine=front_spine,
        allowed_fact_ids=allowed,
        excluded_refs=list(c04.get("excluded_fact_ids") or []),
        retrieval_plan=plan,
        product_hybrid=product_hybrid,
    )
    c05_fact_vectors = maybe_upsert_c05_fact_vector_write_back_atoms(
        c05,
        section_id=section_id,
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        run_id=run_id,
    )
    if c05_fact_vectors.get("attempted") or c05_fact_vectors.get("atom_count"):
        c05["fact_vectors_write_back"] = c05_fact_vectors
    vector_query = normalize_c02_vector_query_receipt(
        dict(c05.get("c02_vector_query") or {}),
        section_id=section_id,
    )
    vector_query["chroma_write_in_c02"] = section_chroma_write_in_c02()
    vector_query["fact_vector_index_preflight_status"] = fact_index_preflight.get("status")
    vector_query["fact_vector_index_preflight_ref"] = (
        fact_vector_index_preflight.FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT
    )
    c05["c02_vector_query"] = vector_query
    c05["fact_vector_index_preflight"] = fact_index_preflight
    c05["fact_vector_index_preflight_ref"] = (
        fact_vector_index_preflight.FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT
    )
    _write_json(artifact_dir / C02_VECTOR_QUERY_ARTIFACT, vector_query)

    # C0 PROPOSES (not commits): emit the per-section intent vector + query output as an inert
    # durable artifact. Post-Exit UWG -> L4 reads this and attaches it to the L4 namespace
    # object + governed Chroma read surface (apps_rg/cache/r1b_governed_receipt_emission.py).
    from apps_rg.runtime.c0.c02_semantic_cache_payload import (
        build_c02_semantic_cache_payload,
        write_c02_semantic_cache_payload,
    )

    _sc_company = ""
    if isinstance(app_payload, dict):
        _sc_company = str(app_payload.get("target_company") or app_payload.get("company") or "")
    _sc_jd_digest = hashlib.sha256((jd_text or "").encode("utf-8")).hexdigest()[:32] if jd_text else ""
    _sc_payload = build_c02_semantic_cache_payload(
        section_id=section_id,
        atoms=atoms,
        vector_query_receipt=vector_query,
        target_company=_sc_company,
        target_role=target_role,
        jd_digest=_sc_jd_digest,
        run_id=run_id,
    )
    write_c02_semantic_cache_payload(artifact_dir, _sc_payload)
    c02["c02_semantic_cache_payload_present"] = True
    c02["c02_semantic_cache_intent_digest"] = _sc_payload.get("intent_digest", "")

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

    from apps_rg.runtime.spine.section_c0_retrieve import (
        assert_no_stop_as_evidence_gap,
        grounding_required_for_section,
    )

    if front_spine is not None:
        assert_no_stop_as_evidence_gap(
            grounding_required=grounding_required_for_section(front_spine),
            fec=fec,
            section_id=section_id,
        )
    c06 = {
        "schema_version": "c06_weak_refine_v1",
        "disabled": True,
        "reason": "receipt_only_refine_removed_use_bounded_c02_retry_when_implemented",
    }
    from apps_rg.runtime.c0.c03_graph_ref_policy import (
        build_graph_targeting_for_pa,
        collect_receipt_only_json_expansion_refs,
    )

    projection = dict(c03.get("role_family_projection") or {})
    receipt_only_json: list[str] = []
    if section_id == "executive_summary":
        from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph

        graph_doc = load_augmented_skills_graph(repo_root=REPO_ROOT)
        receipt_only_json = collect_receipt_only_json_expansion_refs(
            graph_doc, selected_fact_ids=set(allowed)
        )
    graph_targeting_pa = build_graph_targeting_for_pa(
        bindings=bindings,
        role_family_projection=projection,
        receipt_only_lineage_refs=receipt_only_json,
    )
    runtime_payload["graph_targeting_for_pa"] = graph_targeting_pa
    if c04.get("exec_summary_compression"):
        runtime_payload["c04_exec_summary_compression"] = c04.get("exec_summary_compression")
    runtime_payload["fact_vector_index_preflight"] = fact_index_preflight
    runtime_payload["fact_vector_index_preflight_ref"] = (
        fact_vector_index_preflight.FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT
    )

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
    pa_meta["claim_support_graph_refs"] = list(graph_targeting_pa.get("claim_support_graph_refs") or [])
    pa_meta["targeting_graph_refs"] = list(graph_targeting_pa.get("targeting_graph_refs") or [])
    pa_meta["receipt_only_lineage_refs"] = list(graph_targeting_pa.get("receipt_only_lineage_refs") or [])
    pa_meta["graph_expansion_refs"] = list(receipt_only_json)
    pa_meta["receipt_only_json_expansion_excluded_from_pa"] = True
    pa_meta["role_family_projection"] = projection
    authority = bridge_authority_fields()
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
        "proof_pool_digest": canonical.pool_digest,
        "canonical_evidence_set_digest": canonical.pool_digest,
        "fec_allowed_fact_ids_digest": canonical_evidence_set_digest(allowed),
        "source_fact_ids": allowed,
        "allowed_fact_ids": allowed,
        "id_alias_map": dict(canonical.alias_map),
        "fec_materialization_receipt": fec_materialization_receipt,
        "evidence_items": evidence_items,
        "citation_lineage_refs": [
            str(b.get("lineage_refs", [""])[0]) for b in bindings if b.get("lineage_refs")
        ],
        "graph_lineage_refs": [f"graph:{b['fact_id']}" for b in bindings],
        "claim_support_graph_refs": list(graph_targeting_pa.get("claim_support_graph_refs") or []),
        "targeting_graph_refs": list(graph_targeting_pa.get("targeting_graph_refs") or []),
        "receipt_only_lineage_refs": list(graph_targeting_pa.get("receipt_only_lineage_refs") or []),
        "graph_expansion_refs": list(receipt_only_json),
        "graph_targeting_for_pa": graph_targeting_pa,
        "srfs_ref": pool.srfs_ref if pool.srfs_present else "",
        "support_status": fec.support_status or support_status,
        "canonical_c0_2_claimed": True,
        "apps_rg_c03_skills_graph_used": True,
        "core_c03_graph_rag_used": False,
        "canonical_c0_3_claimed": False,
        "canonical_c0_5_claimed": True,
        "fec_shape_only": False,
        **authority,
        "fact_vector_index_preflight_ref": fact_vector_index_preflight.FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT,
        "fact_vector_index_preflight_status": fact_index_preflight.get("status"),
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
            "c03": c03,
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
    from apps_rg.runtime.spine.c0_fec_compose import emit_spine_c0_fec_artifacts

    bridge = SectionFecBridge(section_id=section_id, bridge_doc=bridge_doc)
    apply_canonical_section_evidence_materialization(
        pool=pool,
        runtime_payload=runtime_payload,
        bridge=bridge,
        fec_allowed=allowed,
        fec_materialization_receipt=fec_materialization_receipt,
    )
    runtime_payload["section_fec_bridge"] = bridge.bridge_doc
    runtime_payload["fec_bridge_ref"] = FEC_BRIDGE_ARTIFACT
    runtime_payload["final_evidence_contract_ref"] = FEC_BRIDGE_ARTIFACT
    runtime_payload["c0_fec_bridge_receipt_ref"] = FEC_BRIDGE_RECEIPT
    runtime_payload["canonical_final_evidence_contract_snapshot"] = bridge.bridge_doc.get(
        "final_evidence_contract_snapshot"
    )
    runtime_payload["raw_proof_pool_direct_to_pa"] = False
    runtime_payload["product_visible"] = True
    runtime_payload["c0_authority_mode"] = authority["c0_authority_mode"]
    emit_spine_c0_fec_artifacts(artifact_dir, bridge)
    return bridge


__all__ = [
    "C0_ROOM_RECEIPT",
    "run_section_c0_evidence_room",
    "section_c0_evidence_room_enabled",
]
