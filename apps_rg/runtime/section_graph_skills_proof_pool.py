"""Shared graph-skills fact allocation for apps_rg canonical sections (P2 all-section)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.candidate_fact_ledger import (
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS, select_candidate_facts_for_role

GRAPH_SKILLS_AUTHORITY_SECTIONS: frozenset[str] = frozenset(SECTION_KEYS)

_SECTION_COMPANY_HINTS: dict[str, tuple[str, ...]] = {
    "ibm_bullets": ("ibm",),
    "ibm_narrative": ("ibm",),
    "unify_bullets": ("unify",),
    "unify_narrative": ("unify",),
}

_SECTION_MIN_FACTS: dict[str, int] = {
    "ibm_bullets": 6,
    "ibm_narrative": 6,
    "unify_bullets": 6,
    "unify_narrative": 6,
}


def assert_graph_skills_section(section_id: str) -> None:
    if section_id not in GRAPH_SKILLS_AUTHORITY_SECTIONS:
        raise ValueError(f"not a graph-skills authority section: {section_id!r}")


def allocate_section_facts_from_graph_substrate(
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
    """Role-targeted fact slice for graph-skills proof (substrate ledger is not skills authority)."""
    from apps_rg.runtime.proof_pool_resolver import (
        _ledger_company_hint_slice,
        _sanitize_plan,
        _slice_to_plan_fact,
        _stamp_unify_canonical_bullet_ids,
    )

    assert_graph_skills_section(section_id)
    if section_id == "competencies":
        raise ValueError("competencies uses track-weighted graph expansion, not role slice allocation")

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
    hints = _SECTION_COMPANY_HINTS.get(section_id)
    min_required = _SECTION_MIN_FACTS.get(section_id, 0)

    def _hint_if_sufficient() -> tuple[dict[str, Any], list[str], set[str]] | None:
        if not hints:
            return None
        hinted = _ledger_company_hint_slice(
            ledger,
            section_id=section_id,
            hints=hints,
            limit=min_required or 6,
        )
        if hinted is None:
            return None
        plan, ordered, allowed = hinted
        plan = {
            **plan,
            "selection_method": f"augmented_skills_graph_{section_id}_company_hint",
        }
        return _sanitize_plan(plan), ordered, allowed

    if not slice_rows:
        hinted = _hint_if_sufficient()
        if hinted is not None:
            return hinted
        raise ValueError(f"graph-skills allocation produced empty slice for {section_id!r}")

    facts = [_slice_to_plan_fact(sl, section_id=section_id) for sl in slice_rows]
    if min_required and len(facts) < min_required:
        hinted = _hint_if_sufficient()
        if hinted is not None:
            return hinted
        raise ValueError(
            f"graph-skills allocation insufficient for {section_id!r}: {len(facts)} < {min_required}"
        )
    plan = {
        "section_id": section_id,
        "selection_method": f"augmented_skills_graph_{section_id}",
        "facts": facts,
        "required_fact_ids": [str(f.get("fact_id") or "") for f in facts if f.get("fact_id")],
    }
    plan, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    return _sanitize_plan(plan), ordered, allowed


__all__ = [
    "GRAPH_SKILLS_AUTHORITY_SECTIONS",
    "allocate_section_facts_from_graph_substrate",
    "assert_graph_skills_section",
]
