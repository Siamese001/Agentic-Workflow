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
from apps_rg.runtime.sections.selected_role_fact_set import (
    base_proof_pool_metadata,
    broad_skills_ledger_proof_pool_metadata,
    build_allowed_fact_ids_for_plan_facts,
    plan_fact_to_employment_bullet_row,
    resolve_srfs_section_proof_bundle,
    slice_row_to_plan_fact,
)

PROOF_SOURCE_SRFS = "srfs"
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
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    plan = {
        "section_id": section_id,
        "selection_method": f"broad_skills_ledger_{section_id}_company_hint",
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
    }
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
    if not slice_rows:
        hint_map = {
            "ibm_bullets": ("ibm",),
            "ibm_narrative": ("ibm",),
            "unify_narrative": ("unify",),
        }
        limits = {
            "ibm_bullets": 6,
            "ibm_narrative": 6,
            "unify_narrative": 6,
        }
        hints = hint_map.get(section_id)
        if hints:
            hinted = _ledger_company_hint_slice(
                ledger,
                section_id=section_id,
                hints=hints,
                limit=limits.get(section_id, 6),
            )
            if hinted is not None:
                return hinted
        raise ValueError(f"ledger allocation produced empty slice for {section_id!r}")
    facts = [_slice_to_plan_fact(sl, section_id=section_id) for sl in slice_rows]
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    plan = {
        "section_id": section_id,
        "selection_method": f"broad_skills_ledger_{section_id}",
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
    }
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

    srfs_path = str(selected_role_fact_set_path or "").strip()
    if srfs_path:
        plan, ordered, allowed, meta = resolve_srfs_section_proof_bundle(srfs_path, section)
        facts = list(plan.get("facts") or [])
        bullet_rows = [plan_fact_to_employment_bullet_row(f) for f in facts]
        digest = _sha256_hex(json.dumps(plan, sort_keys=True, ensure_ascii=False))
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
    if pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER:
        input_authority_patch["broad_skills_ledger"] = "CLAIM_EVIDENCE"
        input_authority_patch["base_resume"] = "BASE_RESUME_SOURCE"
    elif pool.proof_source == PROOF_SOURCE_SRFS:
        input_authority_patch["selected_role_fact_set"] = "CLAIM_EVIDENCE"
        input_authority_patch["base_resume"] = "BASE_RESUME_SOURCE"
    else:
        input_authority_patch["base_resume"] = "CLAIM_EVIDENCE_FALLBACK"

    return {
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
        },
        "input_refs": {
            "proof_pool_ref": pool.proof_pool_ref,
            "proof_pool_digest": pool.proof_pool_digest,
            "broad_skills_ledger_ref": pool.broad_skills_ledger_ref or None,
            "broad_skills_ledger_digest": pool.broad_skills_ledger_digest or None,
            "srfs_ref": pool.srfs_ref or None,
            "base_resume_override_used": pool.base_resume_override_used,
        },
    }


__all__ = [
    "PROOF_SOURCE_BASE_RESUME_FALLBACK",
    "PROOF_SOURCE_BROAD_SKILLS_LEDGER",
    "PROOF_SOURCE_SRFS",
    "SectionProofPool",
    "proof_pool_usage_ledger_extension",
    "resolve_section_proof_pool",
]
