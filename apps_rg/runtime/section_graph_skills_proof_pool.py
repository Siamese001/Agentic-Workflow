"""Shared graph-skills fact allocation for apps_rg canonical sections (P2 all-section)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.candidate_fact_ledger import (
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS, select_candidate_facts_for_role
from apps_rg.runtime.sections.unify_bullets_graph_evidence import _UNIFY_METRIC_LEDGER_IDS

GRAPH_SKILLS_AUTHORITY_SECTIONS: frozenset[str] = frozenset(SECTION_KEYS)

_SECTION_COMPANY_HINTS: dict[str, tuple[str, ...]] = {
    "ibm_bullets": ("ibm",),
    "ibm_narrative": ("ibm",),
    "unify_narrative": ("unify",),
    "insurtech_bullets": ("insur", "policy administration"),
    "insurtech_narrative": ("insur", "policy administration"),
    "ey_bullets": ("ey", "ernst", "young", "regulatory", "audit"),
    "ey_narrative": ("ey", "ernst", "young", "regulatory", "audit"),
}

_SECTION_MIN_FACTS: dict[str, int] = {
    "ibm_bullets": 6,
    "ibm_narrative": 6,
    "unify_bullets": 6,
    "unify_narrative": 6,
    "insurtech_bullets": 3,
    "insurtech_narrative": 3,
    "ey_bullets": 3,
    "ey_narrative": 3,
}


def _ledger_rows_matching_company_hints(ledger: dict[str, Any], hints: tuple[str, ...]) -> list[dict[str, Any]]:
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


def _graph_substrate_company_hint_plan(
    ledger: dict[str, Any],
    *,
    section_id: str,
    hints: tuple[str, ...],
    limit: int,
) -> tuple[dict[str, Any], list[str], set[str]] | None:
    """IBM/narrative fallback only — not used for unify_bullets (see graph-ranked plan)."""
    if section_id == "unify_bullets":
        raise ValueError(
            "company_hint allocation is forbidden for unify_bullets; "
            "use augmented_skills_graph_unify_bullets_track_ranked"
        )
    from apps_rg.runtime.sections.selected_role_fact_set import slice_row_to_plan_fact

    from apps_rg.runtime.proof_pool_resolver import _stamp_unify_canonical_bullet_ids

    rows = _ledger_rows_matching_company_hints(ledger, hints)
    if not rows:
        return None
    rows.sort(key=lambda r: str(r.get("candidate_fact_id") or ""))
    picked = rows[:limit]
    facts = [slice_row_to_plan_fact(r, section_id=section_id) for r in picked]
    plan = {
        "section_id": section_id,
        "selection_method": f"augmented_skills_graph_{section_id}_company_hint",
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
    }
    plan, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    return {k: v for k, v in plan.items() if not str(k).startswith("_")}, ordered, allowed


def _fact_scores_from_graph_expansion(
    expansion: dict[str, Any],
    *,
    unify_ledger_ids: set[str],
) -> dict[str, float]:
    """Rank ledger facts by track-weighted graph expansion order (higher = stronger)."""
    scores: dict[str, float] = {}
    selected_facts = list(expansion.get("selected_facts") or [])
    n = max(len(selected_facts), 1)
    for i, fe in enumerate(selected_facts):
        if not isinstance(fe, dict):
            continue
        cid = str(fe.get("fact_id") or "").strip()
        if cid in unify_ledger_ids:
            scores[cid] = max(scores.get(cid, 0.0), float(n - i))
    return scores


def _graph_ranked_unify_bullets_plan(
    ledger: dict[str, Any],
    *,
    section_id: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    limit: int,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], list[str], set[str]] | None:
    """JD/track-weighted graph ranking for Unify bullets — not sorted ledger id[:6]."""
    from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
    from apps_rg.fact_inventory.track_weighted_graph_expansion import (
        build_track_weighted_expansion,
        infer_projection_role_family_key,
    )
    from apps_rg.runtime.proof_pool_resolver import _stamp_unify_canonical_bullet_ids
    from apps_rg.runtime.sections.selected_role_fact_set import slice_row_to_plan_fact

    unify_rows = _ledger_rows_matching_company_hints(ledger, ("unify",))
    if not unify_rows:
        return None
    by_id = {str(r.get("candidate_fact_id") or "").strip(): r for r in unify_rows}
    by_id = {k: v for k, v in by_id.items() if k}

    root = repo_root or Path(__file__).resolve().parents[2]
    graph = load_augmented_skills_graph(repo_root=root)
    role_key = infer_projection_role_family_key(
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
    )
    expansion = build_track_weighted_expansion(
        graph=graph,
        role_family_key=role_key,
        jd_text=jd_text,
        briefing_text=briefing_text,
        repo_root=root,
        min_tracks_with_facts=1,
    )
    scores = _fact_scores_from_graph_expansion(expansion, unify_ledger_ids=set(by_id.keys()))

    picked_ids: list[str] = []
    for fid in _UNIFY_METRIC_LEDGER_IDS:
        if fid in by_id and fid not in picked_ids:
            picked_ids.append(fid)
    ranked = sorted(
        by_id.keys(),
        key=lambda fid: (-scores.get(fid, 0.0), fid),
    )
    for fid in ranked:
        if len(picked_ids) >= limit:
            break
        if fid not in picked_ids:
            picked_ids.append(fid)

    if len(picked_ids) < limit:
        return None

    from apps_rg.runtime.sections.unify_bullets_graph_evidence import is_legacy_six_pack_ledger_order

    if is_legacy_six_pack_ledger_order(picked_ids[:limit]):
        # Graph scores tied at zero — fail closed rather than emit legacy six-pack.
        graph_scored = [fid for fid in ranked if scores.get(fid, 0.0) > 0.0]
        picked_ids = []
        for fid in _UNIFY_METRIC_LEDGER_IDS:
            if fid in by_id and fid not in picked_ids:
                picked_ids.append(fid)
        for fid in graph_scored:
            if len(picked_ids) >= limit:
                break
            if fid not in picked_ids:
                picked_ids.append(fid)
        for fid in ranked:
            if len(picked_ids) >= limit:
                break
            if fid not in picked_ids:
                picked_ids.append(fid)
        if len(picked_ids) < limit or is_legacy_six_pack_ledger_order(picked_ids[:limit]):
            return None

    from apps_rg.runtime.sections.unify_bullets_graph_evidence import assign_unify_metric_anchor_slots

    ledger_pick_order = list(picked_ids[:limit])
    facts = [slice_row_to_plan_fact(by_id[fid], section_id=section_id) for fid in ledger_pick_order]
    facts = assign_unify_metric_anchor_slots(facts)
    plan = {
        "section_id": section_id,
        "selection_method": "augmented_skills_graph_unify_bullets_track_ranked",
        "ledger_pick_order": ledger_pick_order,
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
        "_graph_expansion_role_family_key": role_key,
    }
    plan, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    clean = {k: v for k, v in plan.items() if not str(k).startswith("_")}
    return clean, ordered, allowed


def _graph_ranked_ibm_bullets_plan(
    ledger: dict[str, Any],
    *,
    section_id: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    limit: int,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], list[str], set[str]] | None:
    """Phase 2 track-only graph ranking for IBM bullets (2017–2022 employment window)."""
    from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
    from apps_rg.fact_inventory.track_weighted_graph_expansion import (
        build_track_weighted_expansion,
        infer_projection_role_family_key,
    )
    from apps_rg.runtime.proof_pool_resolver import _stamp_unify_canonical_bullet_ids
    from apps_rg.runtime.sections.ibm_bullets_graph_evidence import (
        IBM_BULLETS_MIN_PHASE2_FACTS,
        IBM_EMPLOYMENT_WINDOW_LABEL,
        IBM_PHASE2_CAREER_TRACK,
        IBM_PHASE2_TRACK_WEIGHT_OVERRIDE,
        IBM_TRACK_RANKED_SELECTION_METHOD,
        build_ibm_phase2_graph_plan_fact,
    )

    root = repo_root or Path(__file__).resolve().parents[2]
    graph = load_augmented_skills_graph(repo_root=root)
    role_key = infer_projection_role_family_key(
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
    )
    expansion = build_track_weighted_expansion(
        graph=graph,
        role_family_key=role_key,
        jd_text=jd_text,
        briefing_text=briefing_text,
        repo_root=root,
        weight_override=dict(IBM_PHASE2_TRACK_WEIGHT_OVERRIDE),
        min_tracks_with_facts=1,
        enforce_hybrid_contract=False,
    )

    phase2_entries = [
        fe
        for fe in (expansion.get("selected_facts") or [])
        if isinstance(fe, dict)
        and str(fe.get("career_track") or "") == IBM_PHASE2_CAREER_TRACK
        and str(fe.get("fact_id") or "").strip()
    ]
    phase2_fact_ids = {str(fe["fact_id"]).strip() for fe in phase2_entries}
    hop_by_id = {str(fe["fact_id"]): fe for fe in phase2_entries}
    ledger_by_id: dict[str, dict[str, Any]] = {}
    for raw in ledger.get("candidate_facts") or []:
        if not isinstance(raw, dict):
            continue
        cid = str(raw.get("candidate_fact_id") or "").strip()
        if cid:
            ledger_by_id[cid] = raw

    scores = _fact_scores_from_graph_expansion(expansion, unify_ledger_ids=phase2_fact_ids)

    def _rank_key(fid: str) -> tuple[int, float, str]:
        row = ledger_by_id.get(fid) or {}
        blob = " ".join(
            str(row.get(key) or "")
            for key in ("company_lane", "company", "claim_text", "domain_family")
        ).lower()
        ibm_boost = 1 if "ibm" in blob else 0
        return (-ibm_boost, -scores.get(fid, 0.0), fid)

    pick_n = max(IBM_BULLETS_MIN_PHASE2_FACTS, min(limit, len(phase2_fact_ids)))
    picked_ids = sorted(phase2_fact_ids, key=_rank_key)[:pick_n]

    facts: list[dict[str, Any]] = []
    for fid in picked_ids:
        hop = hop_by_id.get(fid) or {}
        fact = build_ibm_phase2_graph_plan_fact(
            fact_id=fid,
            ledger_row=ledger_by_id.get(fid),
            hop_entry=hop,
            graph=graph,
            section_id=section_id,
        )
        if fact:
            facts.append(fact)

    if len(facts) < IBM_BULLETS_MIN_PHASE2_FACTS:
        return None

    plan = {
        "section_id": section_id,
        "selection_method": IBM_TRACK_RANKED_SELECTION_METHOD,
        "ledger_pick_order": picked_ids,
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
        "career_track_scope_allowed": [IBM_PHASE2_CAREER_TRACK],
        "employment_window": IBM_EMPLOYMENT_WINDOW_LABEL,
        "career_track_scope_policy": "phase2_data_tech_cloud_ml_only",
        "_graph_expansion_role_family_key": role_key,
    }
    plan, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    clean = {k: v for k, v in plan.items() if not str(k).startswith("_")}
    return clean, ordered, allowed


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
        _sanitize_plan,
        _slice_to_plan_fact,
        _stamp_unify_canonical_bullet_ids,
    )

    assert_graph_skills_section(section_id)
    if section_id == "competencies":
        raise ValueError("competencies uses track-weighted graph expansion, not role slice allocation")

    min_required = _SECTION_MIN_FACTS.get(section_id, 0)
    repo_root = Path(__file__).resolve().parents[2]

    if section_id == "unify_bullets":
        ranked = _graph_ranked_unify_bullets_plan(
            ledger,
            section_id=section_id,
            target_role=target_role,
            jd_text=jd_text,
            briefing_text=briefing_text,
            limit=min_required or 6,
            repo_root=repo_root,
        )
        if ranked is not None:
            return _sanitize_plan(ranked[0]), ranked[1], ranked[2]

    if section_id == "ibm_bullets":
        from apps_rg.runtime.sections.ibm_bullets_graph_evidence import IBM_BULLETS_MIN_PHASE2_FACTS

        ranked = _graph_ranked_ibm_bullets_plan(
            ledger,
            section_id=section_id,
            target_role=target_role,
            jd_text=jd_text,
            briefing_text=briefing_text,
            limit=min_required or IBM_BULLETS_MIN_PHASE2_FACTS,
            repo_root=repo_root,
        )
        if ranked is not None:
            return _sanitize_plan(ranked[0]), ranked[1], ranked[2]
        raise ValueError(
            "graph-skills allocation for ibm_bullets requires "
            f">={IBM_BULLETS_MIN_PHASE2_FACTS} Phase 2 track facts; ranked plan unavailable"
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
    hints = _SECTION_COMPANY_HINTS.get(section_id)

    def _hint_if_sufficient() -> tuple[dict[str, Any], list[str], set[str]] | None:
        if not hints:
            return None
        hinted = _graph_substrate_company_hint_plan(
            ledger,
            section_id=section_id,
            hints=hints,
            limit=min_required or 6,
        )
        if hinted is None:
            return None
        plan, ordered, allowed = hinted
        fact_count = len(plan.get("facts") or [])
        if min_required and fact_count < min_required:
            if fact_count > 0:
                return plan, ordered, allowed
            return None
        return plan, ordered, allowed

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
    "_graph_ranked_ibm_bullets_plan",
    "_graph_ranked_unify_bullets_plan",
]
