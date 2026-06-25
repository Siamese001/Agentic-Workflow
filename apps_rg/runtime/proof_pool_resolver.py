"""Product section evidence resolution for apps_rg canonical lanes.

Canonical CLI ``python -m apps_rg --section <lane>`` resolves exactly one story authority:
``augmented_skills_graph`` + candidate-fact ledger substrate. Legacy proof-pool modes
(broad skills ledger, SRFS-as-authority, base-resume fallback, prompt pooling) are
deleted from this module — see ``apps_rg.runtime.legacy_proof_sources`` for offline labels only.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    default_taxonomy_path,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.runtime.resume_resolution import ResumeResolutionError, load_lane_base_resume_json
from apps_rg.fact_inventory.augmented_skills_graph import (
    CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
    CLAIM_EVIDENCE_SOURCE_TYPE_BASE_RESUME,
    CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
    claim_evidence_fields,
    load_augmented_skills_graph,
    merge_dual_source_proof_pool_metadata,
    resolve_augmented_skills_graph_authority,
)
from apps_rg.runtime.legacy_proof_sources import PROOF_SOURCE_BROAD_SKILLS_LEDGER
from apps_rg.runtime.sections.graph_evidence_contract import (
    SECTION_KEYS,
    build_allowed_fact_ids_for_plan_facts,
    build_graph_evidence_depth_report,
    graph_only_proof_pool_metadata,
    plan_fact_to_employment_bullet_row,
    require_graph_evidence_depth,
    slice_row_to_plan_fact,
)


def _merge_dual_source_metadata(
    meta: dict[str, Any],
    *,
    repo_root: Path,
    claim_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Attach explicit claim-evidence + skills-authority fields; never alias ledger as skills SSOT."""
    skills = resolve_augmented_skills_graph_authority(repo_root=repo_root)
    return merge_dual_source_proof_pool_metadata(
        meta,
        claim_evidence=claim_evidence,
        skills_authority=skills,
    )

PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH = "augmented_skills_graph"


@dataclass(frozen=True, slots=True)
class SectionProofPool:
    section: str
    proof_source: str
    proof_pool_ref: str
    proof_pool_digest: str
    selected_fact_plan: dict[str, Any]
    allowed_fact_ids_ordered: list[str]
    allowed_fact_ids: set[str]
    bullet_rows: list[dict[str, Any]]
    proof_pool_metadata: dict[str, Any]
    fallback_used: bool
    base_resume_fallback_used: bool
    broad_skills_ledger_present: bool
    srfs_present: bool
    base_resume_json_ref: str
    base_resume_json_hash: str
    broad_skills_ledger_ref: str
    broad_skills_ledger_digest: str
    srfs_ref: str
    base_resume_override_used: bool
    targeting_inputs_used: dict[str, bool] = field(default_factory=dict)


def _sha256_hex(text: str | bytes) -> str:
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()


def _maybe_apply_hybrid_informed_fact_plan_reorder(
    plan: dict[str, Any],
    *,
    section_id: str,
    jd_text: str,
    briefing_text: str,
    target_company: str,
    target_role: str,
) -> dict[str, Any]:
    """W2B: reorder ledger-selected facts by JD hybrid scores when product hybrid is available."""
    from datetime import datetime, timezone

    from apps_rg.runtime.c0.c02_product_hybrid_retrieval import (
        perform_product_hybrid_retrieval,
        product_hybrid_retrieval_required,
        provisional_digest_from_atoms,
    )
    from apps_rg.runtime.c0.hybrid_informed_fact_plan_reorder import (
        apply_hybrid_informed_fact_plan_reorder,
    )
    from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

    if not product_hybrid_retrieval_required(section_id):
        return plan
    facts = list(plan.get("facts") or [])
    atoms = [
        {
            "fact_id": str(f.get("fact_id") or ""),
            "text_to_embed": str(f.get("text") or f.get("claim_text") or ""),
        }
        for f in facts
        if f.get("fact_id")
    ]
    try:
        hybrid = perform_product_hybrid_retrieval(
            section_id=section_id,
            app_payload={
                "jd_text": jd_text,
                "briefing_text": briefing_text,
                "target_company": target_company,
                "target_role": target_role,
            },
            evidence_digest=provisional_digest_from_atoms(atoms),
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
        )
    except C0EvidenceGapError:
        return plan
    return apply_hybrid_informed_fact_plan_reorder(plan, hybrid_doc=hybrid)


def _ledger_path_explicit(path: str | None, *, repo_root: Path) -> Path:
    env_override = str(os.environ.get("APPS_RG_BROAD_SKILLS_LEDGER_PATH") or "").strip()
    if path and str(path).strip():
        p = Path(path)
        return p if p.is_absolute() else (repo_root / p).resolve()
    if env_override:
        p = Path(env_override)
        return p if p.is_absolute() else (repo_root / p).resolve()
    return default_ledger_path(repo_root)


def _slice_to_plan_fact(sl: Any, *, section_id: str) -> dict[str, Any]:
    if isinstance(sl, dict):
        return slice_row_to_plan_fact(sl, section_id=section_id)
    row = {
        "candidate_fact_id": sl.candidate_fact_id,
        "claim_text": sl.claim_text,
        "confidence": sl.confidence,
        "verification_status": sl.verification_status,
        "claim_eligible_medium": sl.claim_eligible_medium,
        "source_trace_archive_relpaths": list(sl.source_trace_archive_relpaths),
        "metric_values": list(sl.metric_values),
        "technologies": list(sl.capability_tags),
        "domain": sl.domain_family,
        "company": sl.company,
        "role_families_supported": list(sl.role_families_supported),
    }
    return slice_row_to_plan_fact(row, section_id=section_id)


def _sanitize_plan(plan: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in plan.items() if not str(k).startswith("_")}


def _stamp_ibm_canonical_bullet_ids(plan: dict[str, Any]) -> tuple[dict[str, Any], list[str], set[str]]:
    """Map ledger ``fact_*`` rows to canonical ``bul_ibm_*`` ids for IBM bullet X2 gates."""
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS

    return _stamp_canonical_surface_ids(plan, canonical_ids=IBM_BULLET_IDS, prefix="bul_ibm_")


def _stamp_role_canonical_bullet_ids(plan: dict[str, Any]) -> tuple[dict[str, Any], list[str], set[str]]:
    """Deprecated role-lane compatibility: preserve graph proof ids unchanged."""
    section_id = str(plan.get("section_id") or "")
    if section_id in ("insurtech_bullets", "insurtech_narrative", "ey_bullets", "ey_narrative"):
        facts = list(plan.get("facts") or [])
        ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
        return plan, ordered, allowed
    facts = list(plan.get("facts") or [])
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    return plan, ordered, allowed


def _stamp_canonical_surface_ids(
    plan: dict[str, Any],
    *,
    canonical_ids: tuple[str, ...],
    prefix: str,
) -> tuple[dict[str, Any], list[str], set[str]]:
    """Map ledger ``fact_*`` rows to canonical surface ids while retaining ledger aliases."""
    facts = list(plan.get("facts") or [])
    if not facts or str(facts[0].get("fact_id") or "").startswith(prefix):
        ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
        return plan, ordered, allowed
    for idx, fact in enumerate(facts[: len(canonical_ids)]):
        if idx >= len(canonical_ids):
            break
        ledger_id = str(fact.get("fact_id") or fact.get("candidate_fact_id") or "").strip()
        if ledger_id:
            fact["ledger_candidate_fact_id"] = ledger_id
        fact["fact_id"] = canonical_ids[idx]
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    stamped = {
        **plan,
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
    }
    return stamped, ordered, allowed


def _stamp_unify_canonical_bullet_ids(plan: dict[str, Any]) -> tuple[dict[str, Any], list[str], set[str]]:
    """Map Unify/IBM ledger rows to canonical surface ids while preserving role-lane graph ids."""
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

    section_id = str(plan.get("section_id") or "")
    if section_id == "ibm_bullets":
        return _stamp_ibm_canonical_bullet_ids(plan)
    if section_id in ("insurtech_bullets", "insurtech_narrative", "ey_bullets", "ey_narrative"):
        facts = list(plan.get("facts") or [])
        ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
        return plan, ordered, allowed
    if section_id not in ("unify_bullets", "unify_narrative"):
        facts = list(plan.get("facts") or [])
        ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
        return plan, ordered, allowed
    facts = list(plan.get("facts") or [])
    if not facts or str(facts[0].get("fact_id") or "").startswith("bul_unify_"):
        ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
        return plan, ordered, allowed
    for idx, fact in enumerate(facts[: len(UNIFY_BULLET_IDS)]):
        if idx >= len(UNIFY_BULLET_IDS):
            break
        ledger_id = str(fact.get("fact_id") or fact.get("candidate_fact_id") or "").strip()
        if ledger_id:
            fact["ledger_candidate_fact_id"] = ledger_id
        fact["fact_id"] = UNIFY_BULLET_IDS[idx]
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    stamped = {
        **plan,
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
    }
    return stamped, ordered, allowed


def _id_alias_map_from_plan(plan: dict[str, Any]) -> dict[str, str]:
    """Surface proof id -> ledger fact id aliases stamped by this resolver."""
    out: dict[str, str] = {}
    for row in plan.get("facts") or []:
        if not isinstance(row, dict):
            continue
        surface = str(row.get("fact_id") or "").strip()
        ledger = str(row.get("ledger_candidate_fact_id") or row.get("candidate_fact_id") or "").strip()
        if surface and ledger and surface != ledger:
            out[surface] = ledger
    return out


def _attach_id_alias_map(meta: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    alias_map = _id_alias_map_from_plan(plan)
    if alias_map:
        return {**meta, "id_alias_map": alias_map}
    return meta


def _resolve_executive_summary_graph_only_proof_pool(
    *,
    root: Path,
    broad_skills_ledger_path: str | None,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    base_ref_str: str,
    base_hash: str,
    override_used: bool,
    targeting: dict[str, bool],
) -> SectionProofPool:
    """Executive summary product proof: augmented skills graph + section graph binding shim only."""
    graph_auth = resolve_augmented_skills_graph_authority(repo_root=root)
    if str(graph_auth.get("skills_authority_status") or "") != "PASS":
        reason = graph_auth.get("skills_authority_block_reason") or "augmented_skills_graph_unavailable"
        raise ValueError(f"executive_summary graph-only authority BLOCKED: {reason}")

    ledger_path = _ledger_path_explicit(broad_skills_ledger_path, repo_root=root)
    ledger_ref_str = (
        str(ledger_path.relative_to(root)) if ledger_path.is_relative_to(root) else str(ledger_path)
    )
    ledger = load_master_candidate_fact_ledger(path=ledger_path)
    taxonomy = load_master_role_family_taxonomy(repo_root=root)
    tax_path = default_taxonomy_path(root)
    graph = load_augmented_skills_graph(repo_root=root)
    graph_ref = str(graph_auth.get("graph_ref") or "")
    graph_digest = str(graph_auth.get("graph_digest") or "")

    from apps_rg.runtime.sections.graph_role_episode_selector import (
        build_selected_graph_evidence_plan_for_section,
    )

    plan, ordered, allowed = build_selected_graph_evidence_plan_for_section(
        repo_root=root,
        section_id="executive_summary",
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
    )
    plan = _sanitize_plan(plan)
    plan = _maybe_apply_hybrid_informed_fact_plan_reorder(
        plan,
        section_id="executive_summary",
        jd_text=jd_text,
        briefing_text=briefing_text,
        target_company=target_company,
        target_role=target_role,
    )
    facts = list(plan.get("facts") or [])
    root_fact_ids = [str(f.get("fact_id") or "") for f in facts if f.get("fact_id")]
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    bullet_rows = [plan_fact_to_employment_bullet_row(f) for f in facts]

    from apps_rg.fact_inventory.track_weighted_graph_expansion import (
        build_track_weighted_expansion,
        infer_projection_role_family_key,
        TrackWeightedExpansionContractError,
    )
    from apps_rg.runtime.c03_graphrag_bound import build_section_c03_graphrag_bound

    role_family_key = infer_projection_role_family_key(
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        taxonomy=taxonomy,
    )
    role_episode_seed_namespace = bool(root_fact_ids) and all(
        fid.startswith("reb_") for fid in root_fact_ids
    )
    try:
        track_expansion = build_track_weighted_expansion(
            graph=graph,
            role_family_key=role_family_key,
            jd_text=jd_text,
            briefing_text=briefing_text,
            seed_fact_ids=root_fact_ids,
            enforce_hybrid_contract=False,
            bind_c03=True,
            repo_root=root,
        )
        track_weighted_seed_fallback_used = False
        track_weighted_seed_fallback_reason = ""
    except TrackWeightedExpansionContractError as exc:
        if not role_episode_seed_namespace:
            raise
        track_expansion = build_track_weighted_expansion(
            graph=graph,
            role_family_key=role_family_key,
            jd_text=jd_text,
            briefing_text=briefing_text,
            seed_fact_ids=[],
            enforce_hybrid_contract=False,
            bind_c03=True,
            repo_root=root,
        )
        track_weighted_seed_fallback_used = True
        track_weighted_seed_fallback_reason = str(exc)

    c03 = build_section_c03_graphrag_bound(
        section_id="executive_summary",
        graph=graph,
        graph_ref=graph_ref,
        graph_digest=graph_digest,
        selected_fact_ids=root_fact_ids,
        role_family_key=role_family_key,
        attach_sqlite_context=True,
        repo_root=root,
    )

    from apps_rg.runtime.c0.c03_allowlist_coherence import (
        build_exec_summary_allowlist_receipt,
        filter_c03_evidence_to_allowed_pool,
    )
    from apps_rg.runtime.c0.exec_summary_graph_targeting_capsule import build_graph_targeting_capsule

    c03, allowlist_filter_receipt = filter_c03_evidence_to_allowed_pool(
        c03,
        allowed,
        track_expansion=track_expansion,
    )
    from apps_rg.runtime.c0.c03_hop_path_materialization import attach_track_weighted_hop_paths_to_c03_bound

    track_expansion_for_hop_paths = None if track_weighted_seed_fallback_used else track_expansion
    c03 = attach_track_weighted_hop_paths_to_c03_bound(
        c03,
        track_expansion_for_hop_paths,
        allowed_fact_ids=allowed,
    )
    graph_targeting_capsule = build_graph_targeting_capsule(
        track_expansion,
        role_family_key=role_family_key,
        allowed_fact_ids=allowed,
    )

    meta = graph_only_proof_pool_metadata(
        section_id="executive_summary",
        candidate_fact_pool_count=len(facts),
        allowed_fact_ids_count=len(allowed),
        graph_ref=graph_ref,
        legacy_ledger_ref=ledger_ref_str,
    )
    meta = {**meta, **graph_auth}
    meta["selected_graph_evidence_plan"] = plan
    meta["track_weighted_seed_fallback_used"] = track_weighted_seed_fallback_used
    meta["track_weighted_seed_fallback_reason"] = track_weighted_seed_fallback_reason
    meta["track_weighted_seed_namespace"] = "role_episode_bundle" if role_episode_seed_namespace else "fact"
    meta["track_weighted_hop_paths_attached_to_c03"] = not track_weighted_seed_fallback_used
    meta["broad_skills_ledger_default"] = False
    meta["broad_skills_ledger_fallback"] = False
    meta["broad_skills_ledger_compatibility_authority"] = False
    meta["broad_skills_ledger_used_as_authority"] = False
    meta["silent_fallback_possible"] = False
    meta["c03_graphrag_bound"] = c03
    meta["graph_targeting_capsule"] = graph_targeting_capsule
    meta["exec_summary_allowlist_receipt"] = build_exec_summary_allowlist_receipt(
        allowed_fact_ids=allowed,
        allowlist_filter_receipt=allowlist_filter_receipt,
        track_expansion=track_expansion,
        proof_pool_digest="",  # filled after digest computed
        jd_text=jd_text,
    )
    promo = meta["exec_summary_allowlist_receipt"].get("c03_promotion_candidates")
    if isinstance(promo, dict):
        meta["c03_promotion_candidates"] = promo
    meta["allowlist_mismatch"] = False
    meta["c03_expansion_surplus_fact_ids"] = list(
        allowlist_filter_receipt.get("c03_expansion_surplus_fact_ids")
        or allowlist_filter_receipt.get("c03_filtered_out_fact_ids")
        or []
    )
    meta["c03_filtered_out_fact_ids"] = list(allowlist_filter_receipt.get("c03_filtered_out_fact_ids") or [])
    meta["c03_context_fact_ids"] = list(allowlist_filter_receipt.get("c03_context_fact_ids") or [])
    meta["c03_sqlite_attach_status"] = str(c03.get("c03_sqlite_attach_status") or "DEGRADED")
    meta["c03_sqlite_attach_reason"] = str(c03.get("c03_sqlite_attach_reason") or "")
    meta["canonical_c0_3_claimed"] = False
    meta["c03_graph_hop_paths_count"] = c03.get(
        "c03_graph_hop_paths_count",
        c03.get("graph_hop_paths_count", len(c03.get("graph_expansion_refs") or [])),
    )
    meta["graph_hop_paths_by_fact_id"] = c03.get("graph_hop_paths_by_fact_id") or {}
    meta["graph_hop_paths_count_semantics"] = c03.get("graph_hop_paths_count_semantics")
    meta["graph_expansion_mode"] = c03.get("graph_expansion_mode")
    meta["non_graph_evidence_items_count"] = c03.get("non_graph_evidence_items_count", 0)
    meta["c03_graph_bound_status"] = str(c03.get("c03_graphrag_bound_status") or "NOT_BOUND")
    meta["track_weighted_graph_expansion"] = track_expansion
    meta["track_weighted_expansion_receipt_ref"] = (
        "docs/reports/apps_rg/career_track_p1_w4_track_weighted_expansion_receipt.json"
    )
    for _c03_key in (
        "c03_graph_bound_status",
        "c03_binding_surface",
        "c03_graph_expansion_ref",
        "c03_graph_hop_paths_count",
        "c03_selected_tracks",
        "c03_selected_fact_ids",
        "c03_selected_skill_ids",
        "non_graph_evidence_items_count",
        "graph_expansion_mode",
        "graph_hop_edge_types_used",
    ):
        if _c03_key in track_expansion:
            meta[f"track_weighted_{_c03_key}"] = track_expansion[_c03_key]
    meta["final_evidence_contract_snapshot"] = c03.get("final_evidence_contract_snapshot")
    for _c03_key in (
        "c03_graphrag_bound_status",
        "graph_expansion_allowed",
        "graph_expansion_refs",
        "graph_lineage_refs",
        "graph_sig",
        "support_status",
        "support_target_met",
        "evidence_items_count",
    ):
        if _c03_key in c03:
            meta[_c03_key] = c03[_c03_key]
    meta = _merge_dual_source_metadata(
        meta,
        repo_root=root,
        claim_evidence=claim_evidence_fields(
            source_type=CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
            source_ref=graph_ref,
            source_digest=graph_digest,
            substrate_type=CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
            substrate_ref=ledger_ref_str,
        ),
    )
    meta = _attach_id_alias_map(meta, plan)
    meta["graph_evidence_depth_report"] = require_graph_evidence_depth(
        meta,
        section_id="executive_summary",
        packet_key="selected_graph_evidence_plan",
    )
    digest = _sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))
    receipt = meta.get("exec_summary_allowlist_receipt")
    if isinstance(receipt, dict):
        receipt["proof_pool_digest"] = digest
    return SectionProofPool(
        section="executive_summary",
        proof_source=PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        proof_pool_ref=graph_ref,
        proof_pool_digest=digest,
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=ordered,
        allowed_fact_ids=allowed,
        bullet_rows=bullet_rows,
        proof_pool_metadata=meta,
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref=base_ref_str,
        base_resume_json_hash=base_hash,
        broad_skills_ledger_ref=ledger_ref_str,
        broad_skills_ledger_digest=_sha256_hex(
            json.dumps(ledger, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        ),
        srfs_ref="",
        base_resume_override_used=override_used,
        targeting_inputs_used=targeting,
    )


def _resolve_generic_section_graph_skills_proof_pool(
    *,
    section_id: str,
    root: Path,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    base_ref_str: str,
    base_hash: str,
    override_used: bool,
    targeting: dict[str, bool],
) -> SectionProofPool:
    """Graph-skills product proof for headline / unify_* / ibm_* (P2 all-section)."""
    from apps_rg.runtime.c03_graphrag_bound import build_section_c03_graphrag_bound
    from apps_rg.runtime.section_graph_skills_proof_pool import (
        allocate_section_facts_from_graph_substrate,
    )

    graph_auth = resolve_augmented_skills_graph_authority(repo_root=root)
    if str(graph_auth.get("skills_authority_status") or "") != "PASS":
        reason = graph_auth.get("skills_authority_block_reason") or "augmented_skills_graph_unavailable"
        raise ValueError(f"{section_id} graph-skills proof pool BLOCKED: {reason}")

    ledger_path = default_ledger_path(root)
    ledger_ref_str = (
        str(ledger_path.relative_to(root)) if ledger_path.is_relative_to(root) else str(ledger_path)
    )
    ledger = load_master_candidate_fact_ledger(path=ledger_path)
    taxonomy = load_master_role_family_taxonomy(repo_root=root)
    tax_path = default_taxonomy_path(root)
    graph = load_augmented_skills_graph(repo_root=root)
    graph_ref = str(graph_auth.get("graph_ref") or "")
    graph_digest = str(graph_auth.get("graph_digest") or "")

    plan, ordered, allowed = allocate_section_facts_from_graph_substrate(
        ledger=ledger,
        taxonomy=taxonomy,
        section_id=section_id,
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        ledger_path=ledger_path,
        taxonomy_path=tax_path,
    )
    facts = list(plan.get("facts") or [])
    root_fact_ids = [str(f.get("fact_id") or "") for f in facts if f.get("fact_id")]
    bullet_rows = [plan_fact_to_employment_bullet_row(f) for f in facts]

    c03_doc = build_section_c03_graphrag_bound(
        section_id=section_id,
        graph=graph,
        graph_ref=graph_ref,
        graph_digest=graph_digest,
        selected_fact_ids=root_fact_ids,
    )
    c03_status = str(c03_doc.get("c03_graphrag_bound_status") or "NOT_BOUND")
    if int(c03_doc.get("non_graph_evidence_items_count") or 0) > 0:
        c03_status = "NOT_BOUND"

    meta = graph_only_proof_pool_metadata(
        section_id=section_id,
        candidate_fact_pool_count=len(facts),
        allowed_fact_ids_count=len(allowed),
        graph_ref=graph_ref,
        legacy_ledger_ref=ledger_ref_str,
    )
    meta = {**meta, **graph_auth}
    meta["selected_graph_evidence_plan"] = plan
    meta["graph_skills_proof_pool"] = True
    meta["graph_skills_proof_pool_wave"] = "P2-ACCELERATED"
    meta["broad_skills_ledger_default"] = False
    meta["broad_skills_ledger_fallback"] = False
    meta["broad_skills_ledger_compatibility_authority"] = False
    meta["broad_skills_ledger_used_as_authority"] = False
    meta["silent_fallback_possible"] = False
    meta["fail_closed_if_graph_unavailable"] = True
    meta["selection_method"] = plan.get("selection_method")
    for scope_key in (
        "career_track_scope_allowed",
        "employment_window",
        "career_track_scope_policy",
        "ledger_pick_order",
    ):
        if plan.get(scope_key) is not None:
            meta[scope_key] = plan.get(scope_key)
    if section_id == "ibm_bullets" and plan.get("career_track_scope_allowed"):
        meta["selected_tracks"] = list(plan.get("career_track_scope_allowed") or [])
    if section_id in ("ibm_bullets", "ibm_narrative"):
        from apps_rg.runtime.sections.ibm_role_episode_evidence import (
            attach_role_episode_bundles_to_proof_pool_metadata,
        )

        meta = attach_role_episode_bundles_to_proof_pool_metadata(
            meta, section_id=section_id, repo_root=root
        )
    if section_id in ("unify_bullets", "unify_narrative"):
        from apps_rg.runtime.sections.unify_role_episode_evidence import (
            attach_role_episode_bundles_to_proof_pool_metadata as _attach_unify_reb,
        )

        meta = _attach_unify_reb(meta, section_id=section_id, repo_root=root)
    if section_id in ("insurtech_bullets", "insurtech_narrative"):
        from apps_rg.runtime.sections.insurtech_role_episode_evidence import (
            attach_role_episode_bundles_to_proof_pool_metadata as _attach_insurtech_reb,
        )

        meta = _attach_insurtech_reb(meta, section_id=section_id, repo_root=root)
    if section_id in ("ey_bullets", "ey_narrative"):
        from apps_rg.runtime.sections.ey_role_episode_evidence import (
            attach_role_episode_bundles_to_proof_pool_metadata as _attach_ey_reb,
        )

        meta = _attach_ey_reb(meta, section_id=section_id, repo_root=root)
    if section_id == "headline":
        from apps_rg.runtime.sections.headline_positioning_evidence import (
            attach_headline_positioning_bundles_to_proof_pool_metadata,
        )

        meta = attach_headline_positioning_bundles_to_proof_pool_metadata(
            meta, section_id=section_id, repo_root=root
        )
        meta["graph_evidence_depth_report"] = require_graph_evidence_depth(
            meta,
            section_id="headline",
            packet_key="headline_positioning_section_packet",
        )
    meta["c03_graph_bound_status"] = c03_status
    meta["c03_graphrag_bound"] = c03_doc
    meta["c03_graph_hop_paths_count"] = c03_doc.get("graph_hop_paths_count", 0)
    meta["non_graph_evidence_items_count"] = c03_doc.get("non_graph_evidence_items_count", 0)
    for key in (
        "c03_graphrag_bound_status",
        "graph_expansion_refs",
        "graph_lineage_refs",
        "evidence_items_count",
        "support_status",
    ):
        if key in c03_doc:
            meta[key] = c03_doc[key]
    meta = _merge_dual_source_metadata(
        meta,
        repo_root=root,
        claim_evidence=claim_evidence_fields(
            source_type=CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
            source_ref=graph_ref,
            source_digest=graph_digest,
            substrate_type=CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
            substrate_ref=ledger_ref_str,
        ),
    )
    meta = _attach_id_alias_map(meta, plan)
    ledger_digest = _sha256_hex(
        json.dumps(ledger, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    )
    digest = _sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))
    return SectionProofPool(
        section=section_id,
        proof_source=PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        proof_pool_ref=graph_ref,
        proof_pool_digest=digest,
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=ordered,
        allowed_fact_ids=allowed,
        bullet_rows=bullet_rows,
        proof_pool_metadata=meta,
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref=base_ref_str,
        base_resume_json_hash=base_hash,
        broad_skills_ledger_ref=ledger_ref_str,
        broad_skills_ledger_digest=ledger_digest,
        srfs_ref="",
        base_resume_override_used=override_used,
        targeting_inputs_used=targeting,
    )


def _resolve_competencies_graph_skills_proof_pool(
    *,
    root: Path,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    base_ref_str: str,
    base_hash: str,
    override_used: bool,
    targeting: dict[str, bool],
) -> SectionProofPool:
    """Competencies product proof: augmented_skills_graph only (P2-W1A). No C0.3 BOUND until P2-W2."""
    from apps_rg.fact_inventory.competencies_graph_skills_proof_pool import (
        C03_STATUS_COMPETENCIES_GRAPH_PROOF,
        build_competencies_graph_skills_proof_payload,
    )

    graph_auth = resolve_augmented_skills_graph_authority(repo_root=root)
    if str(graph_auth.get("skills_authority_status") or "") != "PASS":
        reason = graph_auth.get("skills_authority_block_reason") or "augmented_skills_graph_unavailable"
        raise ValueError(f"competencies graph-skills proof pool BLOCKED: {reason}")

    payload = build_competencies_graph_skills_proof_payload(
        repo_root=root,
        jd_text=jd_text,
        target_role=target_role,
        briefing_text=briefing_text,
    )
    from apps_rg.runtime.sections.graph_role_episode_selector import (
        build_selected_graph_evidence_plan_for_section,
    )

    selected_graph_plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=root,
        section_id="competencies",
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
    )
    selected_graph_plan = _sanitize_plan(selected_graph_plan)
    plan = dict(selected_graph_plan)
    facts = list(plan.get("facts") or [])
    if not facts:
        raise ValueError("competencies graph-skills proof pool BLOCKED: canonical graph plan has no facts")
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    bullet_rows = [plan_fact_to_employment_bullet_row(f) for f in facts]

    graph_ref = str(payload.get("graph_source") or graph_auth.get("graph_ref") or "")
    graph_digest = str(graph_auth.get("graph_digest") or "")
    ledger_path = default_ledger_path(root)
    ledger_ref_str = (
        str(ledger_path.relative_to(root)) if ledger_path.is_relative_to(root) else str(ledger_path)
    )
    ledger = load_master_candidate_fact_ledger(path=ledger_path)
    ledger_digest = _sha256_hex(
        json.dumps(ledger, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    )

    meta = graph_only_proof_pool_metadata(
        section_id="competencies",
        candidate_fact_pool_count=len(facts),
        allowed_fact_ids_count=len(allowed),
        graph_ref=graph_ref,
        legacy_ledger_ref=ledger_ref_str,
    )
    meta = {**meta, **graph_auth}
    meta["selected_graph_evidence_plan"] = selected_graph_plan
    meta["canonical_section_graph_plan_id"] = selected_graph_plan.get("plan_id")
    meta["canonical_section_graph_plan_digest"] = selected_graph_plan.get("plan_digest")
    meta["graph_evidence_selection_method"] = selected_graph_plan.get("selection_method")
    meta["selected_graph_skill_rows"] = selected_graph_plan.get("selected_skills") or []
    meta["graph_candidate_decision_ledger"] = selected_graph_plan.get("graph_candidate_decision_ledger") or []
    meta["graph_candidate_receipt"] = selected_graph_plan.get("graph_candidate_receipt") or {}
    meta["graph_traversal_receipt"] = selected_graph_plan.get("graph_traversal_receipt") or {}
    meta["selected_graph_skill_count_by_employer"] = (
        (selected_graph_plan.get("skew_diagnostics") or {}).get("selected_skill_counts_by_employer")
        or {}
    )
    meta["selected_graph_metric_count_by_employer"] = (
        (selected_graph_plan.get("skew_diagnostics") or {}).get("selected_metric_counts_by_employer")
        or {}
    )
    meta["graph_skills_proof_pool"] = True
    meta["graph_skills_proof_pool_wave"] = "P2-W1A"
    meta["competencies_product_authority"] = "augmented_skills_graph"
    meta["broad_skills_ledger_default"] = False
    meta["broad_skills_ledger_fallback"] = False
    meta["broad_skills_ledger_compatibility_authority"] = False
    meta["silent_fallback_possible"] = False
    meta["selection_method"] = payload["selection_method"]
    meta["selected_skill_rows"] = payload["selected_skill_rows"]
    meta["selected_tracks"] = payload["selected_tracks"]
    meta["selected_skill_count_by_track"] = payload["selected_skill_count_by_track"]
    meta["selected_fact_count_by_track"] = payload["selected_fact_count_by_track"]
    meta["broad_skills_ledger_used_as_authority"] = False
    meta["legacy_broad_skills_ledger_path"] = payload.get("legacy_broad_skills_ledger_path")
    te = payload.get("track_expansion") or {}
    te_c03 = str(te.get("c03_graph_bound_status") or "")
    if te_c03 == "BOUND" and int(te.get("c03_graph_hop_paths_count") or 0) > 0:
        meta["c03_graph_bound_status"] = "BOUND"
        meta["c03_graph_hop_paths_count"] = te.get("c03_graph_hop_paths_count", 0)
        meta["non_graph_evidence_items_count"] = 0
    else:
        meta["c03_graph_bound_status"] = C03_STATUS_COMPETENCIES_GRAPH_PROOF
    meta["c03_graphrag_bound_required"] = False
    meta["track_weighted_graph_expansion_ref"] = payload.get("track_weighted_expansion_ref")
    meta["track_weighted_tracks_with_facts"] = te.get("tracks_with_facts")
    meta["graph_hop_paths_sample"] = payload.get("graph_hop_paths_sample")
    meta = _merge_dual_source_metadata(
        meta,
        repo_root=root,
        claim_evidence=claim_evidence_fields(
            source_type=CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
            source_ref=graph_ref,
            source_digest=graph_digest,
            substrate_type=CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
            substrate_ref=ledger_ref_str,
        ),
    )
    meta = _attach_id_alias_map(meta, plan)
    from apps_rg.runtime.sections.competency_capability_evidence import (
        attach_competency_bundles_to_proof_pool_metadata,
    )

    meta = attach_competency_bundles_to_proof_pool_metadata(
        meta, section_id="competencies", repo_root=root
    )
    graph_depth_pre_report = selected_graph_plan.get("graph_evidence_depth_pre_report")
    graph_depth_report = selected_graph_plan.get("graph_evidence_depth_post_report") or selected_graph_plan.get(
        "graph_evidence_depth_report"
    )
    if not isinstance(graph_depth_report, dict) or not graph_depth_report:
        graph_depth_report = build_graph_evidence_depth_report(
            meta,
            section_id="competencies",
            packet_key="selected_graph_evidence_plan",
        )
    meta["graph_evidence_depth_pre_report"] = graph_depth_pre_report
    meta["graph_evidence_depth_report"] = graph_depth_report
    meta["graph_evidence_depth_post_report"] = graph_depth_report
    comparison_report = selected_graph_plan.get("graph_evidence_depth_comparison_report")
    if isinstance(comparison_report, dict) and comparison_report:
        meta["graph_evidence_depth_comparison_report"] = comparison_report
    meta["graph_evidence_depth_status"] = graph_depth_report.get("status")
    meta["graph_evidence_depth_summary"] = graph_depth_report.get("summary")
    meta["competency_capability_depth_report"] = build_graph_evidence_depth_report(
        meta,
        section_id="competencies",
        packet_key="competency_capability_section_packet",
    )
    digest = str(selected_graph_plan.get("plan_digest") or "").strip()
    if not digest:
        digest = _sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))
    meta["graph_selection_binding_receipt"] = {
        "schema_version": "graph_selection_binding_receipt_v1",
        "producer": "apps_rg.runtime.proof_pool_resolver._resolve_competencies_graph_skills_proof_pool",
        "section_id": "competencies",
        "canonical_plan_id": selected_graph_plan.get("plan_id"),
        "canonical_plan_digest": selected_graph_plan.get("plan_digest"),
        "selected_fact_plan_digest": digest,
        "proof_pool_digest": digest,
        "selected_graph_plan_is_selected_fact_plan": True,
        "selection_method": selected_graph_plan.get("selection_method"),
        "pass": bool(selected_graph_plan.get("plan_digest")) and bool(facts),
        "human_explanation": (
            "Competencies proof pool uses the selected graph evidence plan itself as the "
            "canonical selected_fact_plan; no second plan is used for X2/X3 graph proof."
        ),
    }
    return SectionProofPool(
        section="competencies",
        proof_source=PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        proof_pool_ref=graph_ref,
        proof_pool_digest=digest,
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=ordered,
        allowed_fact_ids=allowed,
        bullet_rows=bullet_rows,
        proof_pool_metadata=meta,
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref=base_ref_str,
        base_resume_json_hash=base_hash,
        broad_skills_ledger_ref=ledger_ref_str,
        broad_skills_ledger_digest=ledger_digest,
        srfs_ref="",
        base_resume_override_used=override_used,
        targeting_inputs_used=targeting,
    )


def resolve_section_proof_pool(
    *,
    section: str,
    broad_skills_ledger_path: str | None = None,
    base_resume_ref: str | None = None,
    target_company: str = "",
    target_title: str = "",
    target_role: str | None = None,
    jd_text: str = "",
    briefing_text: str = "",
    repo_root: Path | None = None,
    collect_employment_bullets_fn=None,
    front_spine: Any | None = None,
    product_visible: bool | None = None,
    fixture_dev_only_bypass: bool = False,
    non_product_certified: bool = False,
    graph_skills_proof_pool: bool | None = None,
    legacy_broad_skills_ledger: bool = False,
) -> SectionProofPool:
    """Resolve claim-support proof pool for a canonical section lane."""
    from apps_rg.runtime.spine.front_contracts import (
        assert_proof_pool_front_spine_preconditions,
    )

    assert_proof_pool_front_spine_preconditions(
        front_spine=front_spine,
        product_visible=product_visible,
        fixture_dev_only_bypass=fixture_dev_only_bypass,
        non_product_certified=non_product_certified,
    )
    if section not in SECTION_KEYS:
        raise ValueError(f"unknown section: {section!r}")
    root = repo_root or Path(__file__).resolve().parents[2]
    role_eff = str(target_role or target_title or "").strip()
    company_eff = str(target_company or "").strip()
    jd_eff = str(jd_text or "").strip()
    br_eff = str(briefing_text or "").strip()
    targeting = {
        "jd_title_company": bool(jd_eff or company_eff or role_eff),
        "briefing": bool(br_eff),
    }

    resume_ref = str(base_resume_ref or "").strip() or None
    try:
        base_dict, base_path, base_hash = load_lane_base_resume_json(
            source_resume_ref=resume_ref,
            repo_root=root,
        )
    except ResumeResolutionError:
        base_dict, base_path, base_hash = load_lane_base_resume_json(repo_root=root)
    base_ref_str = str(base_path.relative_to(root)) if base_path.is_relative_to(root) else str(base_path)
    override_used = bool(resume_ref)

    cand_ledger_default = default_ledger_path(root)
    cand_ledger_ref = (
        str(cand_ledger_default.relative_to(root))
        if cand_ledger_default.is_relative_to(root)
        else str(cand_ledger_default)
    )

    from apps_rg.runtime.product_evidence_authority import (
        ProductEvidenceAuthorityError,
        enforce_product_evidence_authority_for_cli,
    )

    if legacy_broad_skills_ledger:
        _legacy_msg = (
            f"{section} product proof authority is augmented_skills_graph only; "
            "legacy_broad_skills_ledger is not permitted"
        )
        if product_visible:
            raise ProductEvidenceAuthorityError(_legacy_msg)
        raise ValueError(_legacy_msg)

    def _finalize_product_pool(raw: SectionProofPool) -> SectionProofPool:
        if product_visible:
            return enforce_product_evidence_authority_for_cli(raw)
        return raw

    try:
        return _resolve_section_proof_pool_inner(
            section=section,
            broad_skills_ledger_path=broad_skills_ledger_path,
            root=root,
            company_eff=company_eff,
            role_eff=role_eff,
            jd_eff=jd_eff,
            br_eff=br_eff,
            base_ref_str=base_ref_str,
            base_hash=base_hash,
            override_used=override_used,
            targeting=targeting,
            front_spine=front_spine,
            product_visible=product_visible,
            finalize_product_pool=_finalize_product_pool,
        )
    except ValueError as exc:
        if product_visible:
            raise ProductEvidenceAuthorityError(str(exc)) from exc
        raise


def _resolve_section_proof_pool_inner(
    *,
    section: str,
    broad_skills_ledger_path: str | None,
    root: Path,
    company_eff: str,
    role_eff: str,
    jd_eff: str,
    br_eff: str,
    base_ref_str: str,
    base_hash: str,
    override_used: bool,
    targeting: dict[str, bool],
    front_spine: Any | None,
    product_visible: bool | None,
    finalize_product_pool: Any,
) -> SectionProofPool:
    if section == "competencies":
        from apps_rg.runtime.native_c03_skills_graph import enrich_proof_pool_with_native_c03

        pool = _resolve_competencies_graph_skills_proof_pool(
            root=root,
            target_company=company_eff,
            target_role=role_eff,
            jd_text=jd_eff,
            briefing_text=br_eff,
            base_ref_str=base_ref_str,
            base_hash=base_hash,
            override_used=override_used,
            targeting=targeting,
        )
        pool = enrich_proof_pool_with_native_c03(
            pool, front_spine=front_spine, repo_root=root
        )
        return finalize_product_pool(pool)

    if section == "executive_summary":
        pool = _resolve_executive_summary_graph_only_proof_pool(
            root=root,
            broad_skills_ledger_path=broad_skills_ledger_path,
            target_company=company_eff,
            target_role=role_eff,
            jd_text=jd_eff,
            briefing_text=br_eff,
            base_ref_str=base_ref_str,
            base_hash=base_hash,
            override_used=override_used,
            targeting=targeting,
        )
        from apps_rg.runtime.native_c03_skills_graph import enrich_proof_pool_with_native_c03

        pool = enrich_proof_pool_with_native_c03(
            pool, front_spine=front_spine, repo_root=root
        )
        return finalize_product_pool(pool)

    return finalize_product_pool(
        _resolve_generic_section_graph_skills_proof_pool(
            section_id=section,
            root=root,
            target_company=company_eff,
            target_role=role_eff,
            jd_text=jd_eff,
            briefing_text=br_eff,
            base_ref_str=base_ref_str,
            base_hash=base_hash,
            override_used=override_used,
            targeting=targeting,
        )
    )


def proof_pool_usage_ledger_extension(pool: SectionProofPool) -> dict[str, Any]:
    """Extra fields merged into section_input_usage_ledger.json."""
    if pool.proof_source != PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH:
        raise ValueError(
            f"{pool.section} product proof_source must be augmented_skills_graph; "
            f"got {pool.proof_source!r}"
        )
    claim_support = ["augmented_skills_graph"]
    input_authority_patch: dict[str, str] = {
        "jd_text": "TARGETING_INPUT",
        "target_title": "POSITIONING_INPUT",
        "target_company": "POSITIONING_INPUT",
        "briefing_research": "CONTEXT_INPUT",
        "selected_fact_plan": "CLAIM_EVIDENCE_AFTER_SELECTION",
        "augmented_skills_graph": "CLAIM_EVIDENCE_AND_SKILLS_AUTHORITY",
        "base_resume": "DEPRECATED_NON_AUTHORITY",
    }
    if pool.broad_skills_ledger_ref:
        input_authority_patch["broad_skills_ledger"] = "DEPRECATED_REFERENCE_ONLY"

    pp_meta = dict(pool.proof_pool_metadata or {})
    skills_status = str(pp_meta.get("skills_source_authority_status") or "")
    skills_authority_patch: dict[str, str] = {}
    if pp_meta.get("augmented_skills_graph_present"):
        skills_authority_patch["augmented_skills_graph"] = "SKILLS_COMPETENCY_AUTHORITY"
    elif skills_status == "BLOCKED":
        skills_authority_patch["augmented_skills_graph"] = "SKILLS_AUTHORITY_BLOCKED"
    if pool.broad_skills_ledger_present:
        skills_authority_patch["broad_skills_ledger"] = "CLAIM_EVIDENCE_ONLY_DEPRECATED_SKILLS_LABEL"
    input_authority_patch = {**input_authority_patch, **skills_authority_patch}

    input_refs = {
        "proof_pool_ref": pool.proof_pool_ref,
        "proof_pool_digest": pool.proof_pool_digest,
        "broad_skills_ledger_ref": pool.broad_skills_ledger_ref or None,
        "broad_skills_ledger_digest": pool.broad_skills_ledger_digest or None,
        "srfs_ref": pool.srfs_ref or None,
        "base_resume_override_used": pool.base_resume_override_used,
    }
    for key in (
        "augmented_skills_graph_ref",
        "augmented_skills_graph_digest",
        "graph_ref",
        "graph_digest",
        "graph_version",
        "legacy_skills_ledger_ref",
    ):
        if pp_meta.get(key):
            input_refs[key] = pp_meta.get(key)

    from apps_rg.runtime.product_evidence_authority import product_section_receipt_authority

    ext: dict[str, Any] = {
        "proof_source": pool.proof_source,
        "proof_pool_ref": pool.proof_pool_ref,
        "proof_pool_digest": pool.proof_pool_digest,
        "product_evidence_authority_receipt": product_section_receipt_authority(pp_meta),
        "jd_title_company_present": bool(pool.targeting_inputs_used.get("jd_title_company")),
        "briefing_present": bool(pool.targeting_inputs_used.get("briefing")),
        "broad_skills_ledger_present": pool.broad_skills_ledger_present,
        "srfs_present": pool.srfs_present,
        "base_resume_fallback_used": pool.base_resume_fallback_used,
        "allowed_source_fact_ids_count": len(pool.allowed_fact_ids),
        "non_proof_inputs": ["jd_title_company", "briefing"],
        "claim_support_inputs": claim_support,
        "input_authority": input_authority_patch,
        "evidence_boundary": {
            "claim_evidence_sources": claim_support,
            "non_evidence_inputs": ["jd_text", "target_title", "target_company", "briefing_research"],
            "skills_competency_authority": "augmented_skills_graph",
        },
        "input_refs": input_refs,
    }
    for key in (
        "source_authority",
        "skills_source_type",
        "skills_source_authority_status",
        "skills_authority_source_type",
        "skills_authority_graph_ref",
        "skills_authority_graph_digest",
        "skills_authority_graph_version",
        "skills_authority_status",
        "claim_evidence_source_type",
        "claim_evidence_source_ref",
        "claim_evidence_source_digest",
        "claim_evidence_substrate_type",
        "claim_evidence_substrate_ref",
        "augmented_skills_graph_present",
        "augmented_skills_graph_ref",
        "augmented_skills_graph_digest",
        "graph_ref",
        "graph_digest",
        "graph_version",
        "legacy_skills_ledger_ref",
        "legacy_skills_ledger_role",
        "legacy_broad_skills_ledger_skills_authority",
        "broad_skills_ledger_claim_evidence_only",
        "broad_skills_ledger_skills_authority",
        "deprecated_non_authority",
        "skills_authority_block_reason",
    ):
        if key in pp_meta:
            ext[key] = pp_meta[key]
    if pp_meta.get("skills_authority_status") in ("BLOCKED", "UNKNOWN", ""):
        ext["skills_authority_x2_boundary"] = "NOT_PASS"
    elif pp_meta.get("skills_authority_status") == "PASS":
        ext["skills_authority_x2_boundary"] = "PASS"
    else:
        ext["skills_authority_x2_boundary"] = "UNKNOWN"
    return ext


__all__ = [
    "PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH",
    "SectionProofPool",
    "proof_pool_usage_ledger_extension",
    "resolve_section_proof_pool",
]
