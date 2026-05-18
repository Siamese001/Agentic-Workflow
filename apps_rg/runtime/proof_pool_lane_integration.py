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
    base_row["authority"] = (ext.get("input_authority") or {}).get(
        "base_resume",
        base_row.get("authority"),
    )
    riu["base_resume"] = base_row
    if pool.broad_skills_ledger_present:
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
    out["required_input_usage"] = riu
    return out


__all__ = ["apply_proof_pool_to_usage_ledger", "load_section_proof_for_lane"]
