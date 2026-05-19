"""Shared section proof-pool resolution for apps_rg canonical lanes.

Resolution order:
1. SelectedRoleFactSet (SRFS) when path supplied
2. Broad skills ledger (default SSOT) when loadable
3. Base resume employment bullets (explicit fallback)
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    default_taxonomy_path,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    SECTION_KEYS,
    SelectedLedgerFactSlice,
    select_candidate_facts_for_role,
)
from apps_rg.runtime.resume_resolution import ResumeResolutionError, load_lane_base_resume_json
from apps_rg.fact_inventory.augmented_skills_graph import (
    CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
    CLAIM_EVIDENCE_SOURCE_TYPE_BASE_RESUME,
    CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
    CLAIM_EVIDENCE_SOURCE_TYPE_SRFS,
    claim_evidence_fields,
    load_augmented_skills_graph,
    merge_dual_source_proof_pool_metadata,
    resolve_augmented_skills_graph_authority,
)
from apps_rg.runtime.sections.selected_role_fact_set import (
    base_proof_pool_metadata,
    broad_skills_ledger_proof_pool_metadata,
    build_allowed_fact_ids_for_plan_facts,
    graph_only_proof_pool_metadata,
    plan_fact_to_employment_bullet_row,
    resolve_srfs_section_proof_bundle,
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

PROOF_SOURCE_SRFS = "srfs"
PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH = "augmented_skills_graph"
PROOF_SOURCE_BROAD_SKILLS_LEDGER = "broad_skills_ledger"
PROOF_SOURCE_BASE_RESUME_FALLBACK = "base_resume_fallback"


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


def _ledger_path_explicit(path: str | None, *, repo_root: Path) -> Path:
    env_override = str(os.environ.get("APPS_RG_BROAD_SKILLS_LEDGER_PATH") or "").strip()
    if path and str(path).strip():
        p = Path(path)
        return p if p.is_absolute() else (repo_root / p).resolve()
    if env_override:
        p = Path(env_override)
        return p if p.is_absolute() else (repo_root / p).resolve()
    return default_ledger_path(repo_root)


def _slice_to_plan_fact(sl: SelectedLedgerFactSlice, *, section_id: str) -> dict[str, Any]:
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


def _ledger_rows_matching_hints(ledger: dict[str, Any], hints: tuple[str, ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in ledger.get("candidate_facts") or []:
        if not isinstance(raw, dict):
            continue
        if str(raw.get("confidence") or "").upper() != "HIGH":
            continue
        blob = " ".join(
            str(raw.get(key) or "")
            for key in ("company_lane", "company", "claim_text", "domain_family")
        ).lower()
        if any(h.lower() in blob for h in hints):
            rows.append(raw)
    return rows


def _stamp_unify_canonical_bullet_ids(plan: dict[str, Any]) -> tuple[dict[str, Any], list[str], set[str]]:
    """Map ledger ``fact_*`` rows to canonical ``bul_unify_*`` ids for X2 bullet gates."""
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

    section_id = str(plan.get("section_id") or "")
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


def _ledger_company_hint_slice(
    ledger: dict[str, Any],
    *,
    section_id: str,
    hints: tuple[str, ...],
    limit: int,
) -> tuple[dict[str, Any], list[str], set[str]] | None:
    rows = _ledger_rows_matching_hints(ledger, hints)
    if not rows:
        return None
    rows.sort(key=lambda r: str(r.get("candidate_fact_id") or ""))
    picked = rows[:limit]
    facts = [slice_row_to_plan_fact(r, section_id=section_id) for r in picked]
    plan = {
        "section_id": section_id,
        "selection_method": f"broad_skills_ledger_{section_id}_company_hint",
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
    }
    plan, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    return plan, ordered, allowed


def _build_competencies_ledger_plan(high_rows: list[dict[str, Any]]) -> dict[str, Any]:
    high = [r for r in high_rows if str(r.get("confidence") or "").upper() == "HIGH"]
    high.sort(
        key=lambda r: (
            -len(r.get("capability_tags") or []),
            str(r.get("candidate_fact_id") or ""),
        )
    )
    picked = high[:24]
    facts = [slice_row_to_plan_fact(r, section_id="competencies") for r in picked]
    if not facts:
        raise ValueError("broad skills ledger has no HIGH facts for competencies slice")
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    return {
        "section_id": "competencies",
        "selection_method": "broad_skills_ledger_competencies",
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
        "_allowed_ordered": ordered,
        "_allowed_set": allowed,
    }


@lru_cache(maxsize=8)
def _cached_role_allocation_key(
    ledger_path: str,
    ledger_digest: str,
    target_company: str,
    target_role: str,
    jd_digest: str,
    briefing_digest: str,
) -> str:
    return "|".join((ledger_path, ledger_digest, target_company, target_role, jd_digest, briefing_digest))


def _allocate_from_ledger(
    *,
    ledger: dict[str, Any],
    taxonomy: dict[str, Any],
    section_id: str,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    ledger_path: Path,
    taxonomy_path: Path,
) -> tuple[dict[str, Any], list[str], set[str]]:
    if section_id == "competencies":
        rows = ledger.get("candidate_facts") or []
        if not isinstance(rows, list):
            raise ValueError("candidate_facts malformed")
        plan = _build_competencies_ledger_plan([r for r in rows if isinstance(r, dict)])
        return _sanitize_plan(plan), list(plan["_allowed_ordered"]), set(plan["_allowed_set"])

    jd_d = _sha256_hex(jd_text.strip())[:64]
    br_d = _sha256_hex(briefing_text.strip())[:64]
    ledger_digest = _sha256_hex(
        json.dumps(ledger, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    )
    cache_key = _cached_role_allocation_key(
        str(ledger_path),
        ledger_digest,
        target_company.strip(),
        target_role.strip(),
        jd_d,
        br_d,
    )
    srfs = select_candidate_facts_for_role(
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        ledger=ledger,
        taxonomy=taxonomy,
        source_ledger_path=str(ledger_path),
        taxonomy_ref=str(taxonomy_path),
    )
    slice_rows = list(srfs.selected_facts_by_section.get(section_id) or [])
    if section_id == "competencies" and not slice_rows:
        rows = ledger.get("candidate_facts") or []
        plan = _build_competencies_ledger_plan([r for r in rows if isinstance(r, dict)])
        return _sanitize_plan(plan), list(plan["_allowed_ordered"]), set(plan["_allowed_set"])
    hint_map = {
        "ibm_bullets": ("ibm",),
        "ibm_narrative": ("ibm",),
        "unify_bullets": ("unify",),
        "unify_narrative": ("unify",),
    }
    min_section_facts = {
        "ibm_bullets": 6,
        "ibm_narrative": 6,
        "unify_bullets": 6,
        "unify_narrative": 6,
    }

    def _company_hint_plan_if_sufficient() -> tuple[dict[str, Any], list[str], set[str]] | None:
        hints = hint_map.get(section_id)
        if not hints:
            return None
        min_required = min_section_facts.get(section_id, 0)
        hinted = _ledger_company_hint_slice(
            ledger,
            section_id=section_id,
            hints=hints,
            limit=min_required or 6,
        )
        if hinted is None:
            return None
        plan, _ordered, _allowed = hinted
        fact_count = len(plan.get("facts") or [])
        if min_required and fact_count < min_required:
            # Ledger-backed company-hint facts still beat base-resume fallback when
            # role allocation is empty or thin (e.g. IBM lane with <6 ledger rows).
            if fact_count > 0:
                return hinted
            return None
        return hinted

    if not slice_rows:
        hinted = _company_hint_plan_if_sufficient()
        if hinted is not None:
            return hinted
        raise ValueError(f"ledger allocation produced empty slice for {section_id!r}")
    facts = [_slice_to_plan_fact(sl, section_id=section_id) for sl in slice_rows]
    min_req = min_section_facts.get(section_id, 0)
    if min_req and len(facts) < min_req:
        hinted = _company_hint_plan_if_sufficient()
        if hinted is not None:
            return hinted
        raise ValueError(
            f"ledger allocation produced insufficient facts for {section_id!r}: {len(facts)} < {min_req}"
        )
    plan = {
        "section_id": section_id,
        "selection_method": f"broad_skills_ledger_{section_id}",
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
    }
    plan, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    return _sanitize_plan(plan), ordered, allowed


def _collect_base_resume_bullets(
    base_resume: dict[str, Any],
    *,
    section_id: str,
    collect_employment_bullets_fn,
) -> tuple[dict[str, Any], set[str], list[dict[str, Any]]]:
    bullet_rows, allowed_fact_ids, _lowers = collect_employment_bullets_fn(base_resume)
    candidate_pool_ids = sorted(allowed_fact_ids)
    if section_id == "executive_summary":
        from apps_rg.runtime.sections.executive_summary_lane import build_selected_fact_plan

        selected = [
            {
                "fact_id": r["fact_id"],
                "claim_text": r["claim_text"],
                "source_employment": r.get("source_employment"),
                "metric_raw": r.get("metric_raw") or "",
                "domain": r.get("domain") or "",
                "technologies": r.get("technologies") or [],
            }
            for r in bullet_rows
        ]
        plan = build_selected_fact_plan(selected)
    else:
        plan = {
            "section_id": section_id,
            "selection_method": "canonical_base_resume_employment_bullets",
            "facts": bullet_rows,
            "required_fact_ids": candidate_pool_ids,
        }
    ordered, allowed_set = build_allowed_fact_ids_for_plan_facts(list(plan.get("facts") or []))
    if not ordered:
        ordered = candidate_pool_ids
        allowed_set = set(allowed_fact_ids)
    return plan, allowed_set, bullet_rows if bullet_rows else [
        plan_fact_to_employment_bullet_row(f) for f in (plan.get("facts") or [])
    ]


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
    """Executive summary product proof: augmented skills graph + C0.3 GraphRAG binding only."""
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

    srfs = select_candidate_facts_for_role(
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        ledger=ledger,
        taxonomy=taxonomy,
        source_ledger_path=str(ledger_path),
        taxonomy_ref=str(tax_path),
    )
    exec_slices = list(srfs.selected_facts_by_section.get("executive_summary") or [])
    if not exec_slices:
        raise ValueError("executive_summary graph-only: arsenal allocation produced empty slice")

    facts = [_slice_to_plan_fact(sl, section_id="executive_summary") for sl in exec_slices]
    plan = {
        "section_id": "executive_summary",
        "selection_method": "augmented_skills_graph_c03_graphrag",
        "facts": facts,
        "required_fact_ids": [str(f.get("fact_id") or "") for f in facts if f.get("fact_id")],
    }
    plan, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    plan = _sanitize_plan(plan)
    bullet_rows = [plan_fact_to_employment_bullet_row(f) for f in facts]

    from apps_rg.runtime.c03_graphrag_bound import build_executive_summary_c03_graphrag_bound

    c03 = build_executive_summary_c03_graphrag_bound(
        graph=graph,
        graph_ref=graph_ref,
        graph_digest=graph_digest,
        selected_fact_ids=ordered,
    )

    meta = graph_only_proof_pool_metadata(
        section_id="executive_summary",
        candidate_fact_pool_count=len(facts),
        allowed_fact_ids_count=len(allowed),
        graph_ref=graph_ref,
        legacy_ledger_ref=ledger_ref_str,
    )
    meta = {**meta, **graph_auth}
    meta["c03_graphrag_bound"] = c03
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
    digest = _sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))
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


def resolve_section_proof_pool(
    *,
    section: str,
    selected_role_fact_set_path: str | None = None,
    broad_skills_ledger_path: str | None = None,
    base_resume_ref: str | None = None,
    target_company: str = "",
    target_title: str = "",
    target_role: str | None = None,
    jd_text: str = "",
    briefing_text: str = "",
    repo_root: Path | None = None,
    collect_employment_bullets_fn=None,
) -> SectionProofPool:
    """Resolve claim-support proof pool for a canonical section lane."""
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

    srfs_path = str(selected_role_fact_set_path or "").strip()
    if section == "executive_summary" and not srfs_path:
        return _resolve_executive_summary_graph_only_proof_pool(
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

    if srfs_path:
        plan, ordered, allowed, meta = resolve_srfs_section_proof_bundle(srfs_path, section)
        facts = list(plan.get("facts") or [])
        bullet_rows = [plan_fact_to_employment_bullet_row(f) for f in facts]
        digest = _sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))
        meta = _merge_dual_source_metadata(
            meta,
            repo_root=root,
            claim_evidence=claim_evidence_fields(
                source_type=CLAIM_EVIDENCE_SOURCE_TYPE_SRFS,
                source_ref=srfs_path,
                source_digest=digest,
                substrate_type=CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
                substrate_ref=cand_ledger_ref,
            ),
        )
        return SectionProofPool(
            section=section,
            proof_source=PROOF_SOURCE_SRFS,
            proof_pool_ref=srfs_path,
            proof_pool_digest=digest,
            selected_fact_plan=plan,
            allowed_fact_ids_ordered=ordered,
            allowed_fact_ids=allowed,
            bullet_rows=bullet_rows,
            proof_pool_metadata=meta,
            fallback_used=False,
            base_resume_fallback_used=False,
            broad_skills_ledger_present=False,
            srfs_present=True,
            base_resume_json_ref=base_ref_str,
            base_resume_json_hash=base_hash,
            broad_skills_ledger_ref="",
            broad_skills_ledger_digest="",
            srfs_ref=srfs_path,
            base_resume_override_used=override_used,
            targeting_inputs_used=targeting,
        )

    ledger_path = _ledger_path_explicit(broad_skills_ledger_path, repo_root=root)
    ledger_ref_str = str(ledger_path.relative_to(root)) if ledger_path.is_relative_to(root) else str(ledger_path)
    try:
        ledger = load_master_candidate_fact_ledger(path=ledger_path)
        taxonomy = load_master_role_family_taxonomy(repo_root=root)
        tax_path = default_taxonomy_path(root)
        ledger_digest = _sha256_hex(
            json.dumps(ledger, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        )
        plan, ordered, allowed = _allocate_from_ledger(
            ledger=ledger,
            taxonomy=taxonomy,
            section_id=section,
            target_company=company_eff,
            target_role=role_eff,
            jd_text=jd_eff,
            briefing_text=br_eff,
            ledger_path=ledger_path,
            taxonomy_path=tax_path,
        )
        plan = _sanitize_plan(plan)
        facts = list(plan.get("facts") or [])
        bullet_rows = [plan_fact_to_employment_bullet_row(f) for f in facts]
        meta = broad_skills_ledger_proof_pool_metadata(
            section_id=section,
            candidate_fact_pool_count=len(facts),
            allowed_fact_ids_count=len(allowed),
            ledger_ref=ledger_ref_str,
        )
        meta = _merge_dual_source_metadata(
            meta,
            repo_root=root,
            claim_evidence=claim_evidence_fields(
                source_type=CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
                source_ref=ledger_ref_str,
                source_digest=ledger_digest,
            ),
        )
        digest = _sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))
        return SectionProofPool(
            section=section,
            proof_source=PROOF_SOURCE_BROAD_SKILLS_LEDGER,
            proof_pool_ref=ledger_ref_str,
            proof_pool_digest=digest,
            selected_fact_plan=plan,
            allowed_fact_ids_ordered=ordered,
            allowed_fact_ids=allowed,
            bullet_rows=bullet_rows,
            proof_pool_metadata=meta,
            fallback_used=False,
            base_resume_fallback_used=False,
            broad_skills_ledger_present=True,
            srfs_present=False,
            base_resume_json_ref=base_ref_str,
            base_resume_json_hash=base_hash,
            broad_skills_ledger_ref=ledger_ref_str,
            broad_skills_ledger_digest=ledger_digest,
            srfs_ref="",
            base_resume_override_used=override_used,
            targeting_inputs_used=targeting,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError):
        pass

    if collect_employment_bullets_fn is None:
        from apps_rg.runtime.dispatch.competencies_dispatch import collect_employment_bullets

        collect_employment_bullets_fn = collect_employment_bullets

    plan, allowed, bullet_rows = _collect_base_resume_bullets(
        base_dict,
        section_id=section,
        collect_employment_bullets_fn=collect_employment_bullets_fn,
    )
    ordered, allowed_set = build_allowed_fact_ids_for_plan_facts(list(plan.get("facts") or []))
    if not ordered:
        ordered = sorted(allowed)
    meta = base_proof_pool_metadata(
        section_id=section,
        candidate_fact_pool_count=len(plan.get("facts") or []),
        allowed_fact_ids_count=len(allowed_set),
        fallback_reason="broad_skills_ledger_unavailable_or_empty",
    )
    meta = _merge_dual_source_metadata(
        meta,
        repo_root=root,
        claim_evidence=claim_evidence_fields(
            source_type=CLAIM_EVIDENCE_SOURCE_TYPE_BASE_RESUME,
            source_ref=base_ref_str,
            source_digest=base_hash,
        ),
    )
    digest = _sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))
    return SectionProofPool(
        section=section,
        proof_source=PROOF_SOURCE_BASE_RESUME_FALLBACK,
        proof_pool_ref=base_ref_str,
        proof_pool_digest=digest,
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=ordered,
        allowed_fact_ids=allowed_set,
        bullet_rows=bullet_rows,
        proof_pool_metadata=meta,
        fallback_used=True,
        base_resume_fallback_used=True,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref=base_ref_str,
        base_resume_json_hash=base_hash,
        broad_skills_ledger_ref=ledger_ref_str,
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=override_used,
        targeting_inputs_used=targeting,
    )


def proof_pool_usage_ledger_extension(pool: SectionProofPool) -> dict[str, Any]:
    """Extra fields merged into section_input_usage_ledger.json."""
    claim_support: list[str] = []
    if pool.proof_source == PROOF_SOURCE_SRFS:
        claim_support = ["srfs"]
    elif pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH:
        claim_support = ["augmented_skills_graph"]
    elif pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER:
        claim_support = ["broad_skills_ledger"]
    else:
        claim_support = ["base_resume_fallback"]

    input_authority_patch: dict[str, str] = {
        "jd_text": "TARGETING_INPUT",
        "target_title": "POSITIONING_INPUT",
        "target_company": "POSITIONING_INPUT",
        "briefing_research": "CONTEXT_INPUT",
        "selected_fact_plan": "CLAIM_EVIDENCE_AFTER_SELECTION",
    }
    if pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH:
        input_authority_patch["augmented_skills_graph"] = "CLAIM_EVIDENCE_AND_SKILLS_AUTHORITY"
        input_authority_patch["base_resume"] = "DEPRECATED_NON_AUTHORITY"
        if pool.broad_skills_ledger_ref:
            input_authority_patch["broad_skills_ledger"] = "DEPRECATED_REFERENCE_ONLY"
    elif pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER:
        input_authority_patch["broad_skills_ledger"] = "CLAIM_EVIDENCE"
        input_authority_patch["base_resume"] = "BASE_RESUME_SOURCE"
    elif pool.proof_source == PROOF_SOURCE_SRFS:
        input_authority_patch["selected_role_fact_set"] = "CLAIM_EVIDENCE"
        input_authority_patch["base_resume"] = "BASE_RESUME_SOURCE"
    else:
        input_authority_patch["base_resume"] = "CLAIM_EVIDENCE_FALLBACK"

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

    ext: dict[str, Any] = {
        "proof_source": pool.proof_source,
        "proof_pool_ref": pool.proof_pool_ref,
        "proof_pool_digest": pool.proof_pool_digest,
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
    "PROOF_SOURCE_BASE_RESUME_FALLBACK",
    "PROOF_SOURCE_BROAD_SKILLS_LEDGER",
    "PROOF_SOURCE_SRFS",
    "SectionProofPool",
    "proof_pool_usage_ledger_extension",
    "resolve_section_proof_pool",
]
