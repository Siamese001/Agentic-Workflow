"""Lane helpers: resolve proof pool + base resume for section execution."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from apps_rg.runtime.proof_pool_resolver import SectionProofPool, resolve_section_proof_pool
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json


def load_section_proof_for_lane(
    *,
    section_id: str,
    args: Any,
    repo_root: Path,
    collect_employment_bullets_fn: Callable[..., Any] | None = None,
) -> tuple[SectionProofPool, dict[str, Any], Path, str]:
    """Return (proof_pool, base_resume_dict, base_path, base_hash) for a lane run."""
    base_ref = str(getattr(args, "base_resume_ref", "") or "").strip() or None
    pool = resolve_section_proof_pool(
        section=section_id,
        selected_role_fact_set_path=str(getattr(args, "selected_role_fact_set", "") or ""),
        broad_skills_ledger_path=str(getattr(args, "broad_skills_ledger_path", "") or "") or None,
        base_resume_ref=base_ref,
        target_company=str(getattr(args, "target_company", "") or ""),
        target_title=str(getattr(args, "target_title", "") or ""),
        target_role=str(getattr(args, "target_role", "") or "") or None,
        jd_text=str(getattr(args, "jd_text", "") or ""),
        briefing_text=str(getattr(args, "briefing", "") or ""),
        repo_root=repo_root,
        collect_employment_bullets_fn=collect_employment_bullets_fn,
    )
    base_dict, base_path, base_hash = load_lane_base_resume_json(
        source_resume_ref=base_ref,
        repo_root=repo_root,
    )
    return pool, base_dict, base_path, base_hash


def apply_proof_pool_to_usage_ledger(doc: dict[str, Any], pool: SectionProofPool) -> dict[str, Any]:
    from apps_rg.runtime.proof_pool_resolver import proof_pool_usage_ledger_extension

    ext = proof_pool_usage_ledger_extension(pool)
    out = dict(doc)
    for key, val in ext.items():
        if key in ("input_authority", "evidence_boundary", "input_refs"):
            continue
        out[key] = val
    out["input_authority"] = {**(out.get("input_authority") or {}), **(ext.get("input_authority") or {})}
    out["evidence_boundary"] = {**(out.get("evidence_boundary") or {}), **(ext.get("evidence_boundary") or {})}
    refs = dict(out.get("input_refs") or {})
    refs.update(ext.get("input_refs") or {})
    out["input_refs"] = refs
    riu = dict(out.get("required_input_usage") or {})
    base_row = dict(riu.get("base_resume") or {})
    base_auth = (ext.get("input_authority") or {}).get("base_resume")
    if base_auth:
        base_row["authority"] = base_auth
        base_row["used"] = base_auth not in (
            "DEPRECATED_NON_AUTHORITY",
            "CLAIM_EVIDENCE_FALLBACK",
        )
    riu["base_resume"] = base_row
    if pool.proof_source == "augmented_skills_graph":
        riu["augmented_skills_graph"] = {
            "required": True,
            "used": True,
            "authority": "CLAIM_EVIDENCE_AND_SKILLS_AUTHORITY",
            "ref": (pool.proof_pool_metadata or {}).get("graph_ref"),
        }
        if pool.broad_skills_ledger_ref:
            riu["legacy_skills_ledger"] = {
                "required": False,
                "used": False,
                "authority": "DEPRECATED_REFERENCE_ONLY",
                "ref": pool.broad_skills_ledger_ref,
            }
    elif pool.broad_skills_ledger_present:
        riu["broad_skills_ledger"] = {
            "required": False,
            "used": True,
            "authority": "CLAIM_EVIDENCE",
            "ref": pool.broad_skills_ledger_ref,
        }
    if pool.srfs_present:
        riu["selected_role_fact_set"] = {
            "required": False,
            "used": True,
            "authority": "CLAIM_EVIDENCE",
            "ref": pool.srfs_ref,
        }
    pp_meta = pool.proof_pool_metadata or {}
    if pp_meta.get("augmented_skills_graph_present"):
        riu["augmented_skills_graph"] = {
            "required": True,
            "used": True,
            "authority": "SKILLS_COMPETENCY_AUTHORITY",
            "ref": pp_meta.get("augmented_skills_graph_ref") or pp_meta.get("graph_ref"),
        }
    elif str(pp_meta.get("skills_source_authority_status") or "") == "BLOCKED":
        riu["augmented_skills_graph"] = {
            "required": True,
            "used": False,
            "authority": "SKILLS_AUTHORITY_BLOCKED",
            "ref": pp_meta.get("augmented_skills_graph_ref") or pp_meta.get("graph_ref"),
        }
    if pp_meta.get("legacy_skills_ledger_ref"):
        riu["legacy_skills_ledger"] = {
            "required": False,
            "used": False,
            "authority": "DEPRECATED_REFERENCE",
            "ref": pp_meta.get("legacy_skills_ledger_ref"),
        }
    claim_type = str(pp_meta.get("claim_evidence_source_type") or "")
    if claim_type:
        riu["claim_evidence"] = {
            "required": True,
            "used": True,
            "authority": "CLAIM_EVIDENCE",
            "source_type": claim_type,
            "ref": pp_meta.get("claim_evidence_source_ref"),
        }
    out["claim_evidence_source_type"] = pp_meta.get("claim_evidence_source_type")
    out["skills_authority_source_type"] = pp_meta.get("skills_authority_source_type")
    out["skills_authority_status"] = pp_meta.get("skills_authority_status")
    out["required_input_usage"] = riu
    return out


__all__ = ["apply_proof_pool_to_usage_ledger", "load_section_proof_for_lane"]
