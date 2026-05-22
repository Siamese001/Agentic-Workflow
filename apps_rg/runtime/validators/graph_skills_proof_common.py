"""Shared graph-skills proof validation (P2-W3). Fail-closed on ledger authority and false C0.3 claims."""
from __future__ import annotations

from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.c03_graphrag_bound import FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF
from apps_rg.runtime.legacy_proof_sources import FORBIDDEN_PRODUCT_PROOF_SOURCES
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH, SectionProofPool

FORBIDDEN_PROOF_SOURCES = FORBIDDEN_PRODUCT_PROOF_SOURCES


class GraphSkillsProofError(ValueError):
    """Graph-skills proof contract violation."""


def assert_pool_not_ledger_authority(pool: SectionProofPool) -> None:
    if pool.proof_source in FORBIDDEN_PROOF_SOURCES:
        raise GraphSkillsProofError(
            f"section {pool.section!r} proof_source={pool.proof_source!r} forbidden for product proof"
        )
    if pool.proof_source != PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH:
        raise GraphSkillsProofError(
            f"section {pool.section!r} must use augmented_skills_graph; got {pool.proof_source!r}"
        )
    meta = pool.proof_pool_metadata or {}
    for flag in (
        "broad_skills_ledger_used_as_authority",
        "broad_skills_ledger_default",
        "broad_skills_ledger_fallback",
        "broad_skills_ledger_compatibility_authority",
    ):
        if meta.get(flag) is True:
            raise GraphSkillsProofError(f"{flag} must be false for {pool.section!r}")
    if pool.fallback_used or pool.base_resume_fallback_used:
        raise GraphSkillsProofError(f"fallback flags set for {pool.section!r}")
    if pool.broad_skills_ledger_present and meta.get("broad_skills_ledger_used_as_authority") is not False:
        raise GraphSkillsProofError(f"broad_skills_ledger_present without deprecation for {pool.section!r}")


def assert_c03_bound_claim_valid(*, section_id: str, meta: dict[str, Any]) -> None:
    status = str(meta.get("c03_graph_bound_status") or meta.get("c03_graphrag_bound_status") or "")
    if status != "BOUND":
        return
    hop_count = int(meta.get("c03_graph_hop_paths_count") or 0)
    if hop_count <= 0:
        c03 = meta.get("c03_graphrag_bound")
        if isinstance(c03, dict):
            hop_count = int(c03.get("graph_hop_paths_count") or len(c03.get("graph_expansion_refs") or []))
    if hop_count <= 0:
        raise GraphSkillsProofError(
            f"{section_id}: c03_graph_bound_status=BOUND without graph_hop_paths_count"
        )
    raw_non_graph = meta.get("non_graph_evidence_items_count")
    non_graph = int(raw_non_graph) if raw_non_graph is not None else 0
    if non_graph != 0:
        raise GraphSkillsProofError(
            f"{section_id}: BOUND claim with non_graph_evidence_items_count={non_graph}"
        )
    c03 = meta.get("c03_graphrag_bound")
    if isinstance(c03, dict):
        support = str(c03.get("support_status") or "")
        if support in FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF:
            raise GraphSkillsProofError(f"{section_id}: forbidden support_status {support!r}")


def assert_skill_rows_graph_supported(skill_rows: list[dict[str, Any]]) -> None:
    for row in skill_rows:
        links = row.get("fact_id_links") or []
        hop = row.get("graph_hop_path") or []
        if not links:
            raise GraphSkillsProofError(f"skill {row.get('skill_id')!r} missing fact_id_links")
        if not hop:
            raise GraphSkillsProofError(f"skill {row.get('skill_id')!r} missing graph_hop_path")


def assert_no_non_graph_evidence(meta: dict[str, Any], *, section_id: str) -> None:
    raw = meta.get("non_graph_evidence_items_count")
    count = int(raw) if raw is not None else 0
    if count > 0:
        raise GraphSkillsProofError(f"{section_id}: non_graph_evidence_items_count={count}")


def validate_section_graph_pool(pool: SectionProofPool) -> dict[str, Any]:
    """Validate a resolved section pool; return summary dict."""
    assert_pool_not_ledger_authority(pool)
    meta = dict(pool.proof_pool_metadata or {})
    assert_c03_bound_claim_valid(section_id=pool.section, meta=meta)
    assert_no_non_graph_evidence(meta, section_id=pool.section)
    skill_rows = meta.get("selected_skill_rows") or []
    if skill_rows:
        assert_skill_rows_graph_supported(list(skill_rows))
    return {
        "section": pool.section,
        "proof_source": pool.proof_source,
        "c03_graph_bound_status": meta.get("c03_graph_bound_status"),
        "broad_skills_ledger_used_as_authority": meta.get("broad_skills_ledger_used_as_authority", False),
        "selection_method": meta.get("selection_method") or pool.selected_fact_plan.get("selection_method"),
    }


__all__ = [
    "GraphSkillsProofError",
    "assert_c03_bound_claim_valid",
    "assert_no_non_graph_evidence",
    "assert_pool_not_ledger_authority",
    "assert_skill_rows_graph_supported",
    "validate_section_graph_pool",
]
