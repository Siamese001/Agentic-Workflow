"""Resolve C0 graph role-family projection from lane targeting inputs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apps_rg.fact_inventory.candidate_fact_ledger import (
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    TAXONOMY_TO_PROJECTION_ROLE,
    infer_projection_role_family_key,
)
if TYPE_CHECKING:
    from apps_rg.runtime.proof_pool_resolver import SectionProofPool
    from apps_rg.runtime.spine.front_contracts import SectionFrontSpineBridge

REPO_DEFAULT_ROLE = "SVP_ENGINEERING_AI_PLATFORM"


def _targeting_from_spine(front_spine: SectionFrontSpineBridge | None) -> tuple[str, str, str]:
    if front_spine is None or front_spine.validated_request is None:
        return "", "", ""
    app = getattr(front_spine.validated_request, "app_payload", None) or {}
    if not isinstance(app, dict):
        return "", "", ""
    target_role = str(
        app.get("target_role") or app.get("target_title") or ""
    ).strip()
    jd_text = str(app.get("job_description_text") or app.get("jd_text") or "").strip()
    briefing = str(app.get("briefing_text") or "").strip()
    return target_role, jd_text, briefing


def resolve_c0_role_family_key(
    *,
    front_spine: SectionFrontSpineBridge | None = None,
    pool: SectionProofPool | None = None,
    repo_root: Any = None,
) -> str:
    """JD-aware projection key for C0.3 graph context (not a static default)."""
    target_role, jd_text, briefing = _targeting_from_spine(front_spine)
    if pool is not None:
        meta = pool.proof_pool_metadata or {}
        if not target_role:
            target_role = str(meta.get("target_role") or "").strip()
        if not jd_text:
            jd_text = str(meta.get("jd_text") or "").strip()
        tw = meta.get("track_weighted_graph_expansion")
        if isinstance(tw, dict) and tw.get("projection_role_family_key"):
            return str(tw["projection_role_family_key"])
    taxonomy = load_master_role_family_taxonomy(repo_root=repo_root)
    key = infer_projection_role_family_key(
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing,
        taxonomy=taxonomy,
    )
    return key or REPO_DEFAULT_ROLE


def resolve_c0_pillar_hints(
    role_family_key: str,
    *,
    taxonomy: dict[str, Any] | None = None,
    repo_root: Any = None,
) -> tuple[str, ...]:
    """Taxonomy proposed_pillar_ids for C0.3 graph binding prioritization."""
    tax = taxonomy or load_master_role_family_taxonomy(repo_root=repo_root)
    projection_to_taxonomy = {v: k for k, v in TAXONOMY_TO_PROJECTION_ROLE.items()}
    tax_id = projection_to_taxonomy.get(role_family_key, role_family_key)
    for row in tax.get("role_families") or []:
        if isinstance(row, dict) and str(row.get("id") or "") == tax_id:
            raw = row.get("proposed_pillar_ids") or []
            return tuple(str(p).strip() for p in raw if str(p).strip())
    return ()


__all__ = ["resolve_c0_role_family_key", "resolve_c0_pillar_hints"]
