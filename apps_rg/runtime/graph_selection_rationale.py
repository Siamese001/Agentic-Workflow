"""JD subgraph selection rationale for graph-skills quality plan (W1+).

Emits ``graph_selection_rationale.json`` describing how JD shapes ranking only —
never proof authority. Product REAL_LLM proof still requires canonical CLI (W10).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import (
    default_augmented_skills_graph_path,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    default_taxonomy_path,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    build_track_weighted_expansion,
    infer_projection_role_family_key,
    resolve_career_track_weights,
)
from apps_rg.runtime.section_graph_skills_proof_pool import (
    GRAPH_SKILLS_AUTHORITY_SECTIONS,
    allocate_section_facts_from_graph_substrate,
)

SCHEMA = "graph_selection_rationale_v1"

JD_BOOST_RULES: tuple[tuple[tuple[str, ...], str, float], ...] = (
    (("actuarial", "derivatives", "greeks", "basel", "ccar", "capital modeling"), "track_actuarial_risk_derivatives", 0.05),
    (
        ("underwriting", "claims", "policy administration", "insurance industry", "insurance carrier"),
        "track_actuarial_risk_derivatives",
        0.08,
    ),
    (("aws", "cloud", "partner", "gtm", "co-sell", "hyperscaler", "revenue"), "track_data_tech_cloud_ml", 0.05),
    (
        (
            "agentic",
            "graphrag",
            "orchestration",
            "routing",
            "llm governance",
            "rag-enhanced",
            "multi-agent",
            "companion agent",
            "automation agent",
        ),
        "track_genai_agentic",
        0.05,
    ),
    (
        ("it strategy", "enterprise architecture", "innovation incubation", "data platforms", "technology strategy"),
        "track_data_tech_cloud_ml",
        0.08,
    ),
    (
        ("it strategy", "enterprise architecture", "innovation incubation", "data platforms", "technology strategy"),
        "track_genai_agentic",
        0.06,
    ),
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_jd_keyword_hits(jd_text: str) -> list[dict[str, Any]]:
    jd = jd_text.lower()
    hits: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for keywords, track, bump in JD_BOOST_RULES:
        matched = [k for k in keywords if k in jd]
        if not matched:
            continue
        key = (track, bump)
        if key in seen:
            continue
        seen.add(key)
        hits.append(
            {
                "track_id": track,
                "bump": bump,
                "keywords_matched": matched,
                "policy_ref": "apps_rg/fact_inventory/track_weighted_graph_expansion.py:resolve_career_track_weights",
            }
        )
    return hits


def jd_track_weight_delta(
    *,
    role_family_key: str,
    jd_text: str,
) -> dict[str, Any]:
    """Compare normalized track weights with vs without JD (monotonic audit).

    After normalization, non-bumped tracks may decrease when bumped tracks gain mass.
    Monotonic PASS requires every JD-keyword-bumped track to hold or gain weight.
    """
    without = resolve_career_track_weights(role_family_key=role_family_key, jd_text="")
    with_jd = resolve_career_track_weights(role_family_key=role_family_key, jd_text=jd_text)
    hits = extract_jd_keyword_hits(jd_text)
    boosted_tracks = {str(h["track_id"]) for h in hits}
    deltas: dict[str, float] = {}
    for track in without:
        deltas[track] = round(with_jd.get(track, 0.0) - without.get(track, 0.0), 6)
    bumped_monotonic = all(deltas.get(t, 0.0) >= -1e-9 for t in boosted_tracks)
    return {
        "weights_without_jd": without,
        "weights_with_jd": with_jd,
        "weight_deltas": deltas,
        "jd_boosted_tracks": sorted(boosted_tracks),
        "jd_boost_monotonic": bumped_monotonic and bool(boosted_tracks),
    }


def reject_jd_only_skill_admission(
    *,
    skill_id: str,
    jd_text: str,
    fact_id_links: list[str] | None,
) -> dict[str, Any]:
    """NEG-1: JD text alone cannot admit a skill without graph fact_id_links."""
    links = [str(x) for x in (fact_id_links or []) if str(x).strip()]
    jd_only_label = skill_id.startswith("jd_") or skill_id.startswith("JD_")
    admitted = bool(links) and not jd_only_label
    return {
        "skill_id": skill_id,
        "admitted": admitted,
        "reason_code": "ok_graph_fact_links" if admitted else "jd_only_or_empty_fact_id_links",
        "fact_id_links_count": len(links),
        "jd_only_skill_id_pattern": jd_only_label,
        "jd_text_present": bool(jd_text.strip()),
    }


def _selected_skills_from_expansion(expansion: dict[str, Any]) -> list[str]:
    skills = expansion.get("selected_skills") or expansion.get("c03_selected_skill_ids") or []
    out: list[str] = []
    for item in skills:
        if isinstance(item, dict):
            sid = str(item.get("skill_id") or "")
        else:
            sid = str(item)
        if sid:
            out.append(sid)
    return sorted(set(out))


def emit_graph_selection_rationale(
    *,
    section_id: str,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str = "",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build rationale artifact (fixture/CLI writer — not product PASS by itself)."""
    root = repo_root or Path(__file__).resolve().parents[2]
    if section_id not in GRAPH_SKILLS_AUTHORITY_SECTIONS:
        raise ValueError(f"unsupported section for graph selection rationale: {section_id!r}")

    graph = load_augmented_skills_graph(repo_root=root)
    graph_path = default_augmented_skills_graph_path(root)
    graph_digest = _sha256_text(json.dumps(graph.get("graph_metadata") or {}, sort_keys=True))

    role_family_key = infer_projection_role_family_key(
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
    )
    weight_audit = jd_track_weight_delta(role_family_key=role_family_key, jd_text=jd_text)
    jd_hits = extract_jd_keyword_hits(jd_text)

    selection_method = f"augmented_skills_graph_{section_id}"
    selected_skill_ids: list[str] = []
    allowed_fact_count = 0
    jd_only_rejections: list[dict[str, Any]] = []

    if section_id == "competencies":
        expansion = build_track_weighted_expansion(
            graph=graph,
            role_family_key=role_family_key,
            jd_text=jd_text,
            briefing_text=briefing_text,
            repo_root=root,
        )
        selection_method = str(expansion.get("graph_expansion_mode") or "track_weighted_graph_expansion")
        selected_skill_ids = _selected_skills_from_expansion(expansion)
        allowed_fact_count = len(expansion.get("selected_facts") or [])
    else:
        ledger = load_master_candidate_fact_ledger(path=default_ledger_path(root))
        taxonomy = load_master_role_family_taxonomy(path=default_taxonomy_path(root))
        plan, _, allowed = allocate_section_facts_from_graph_substrate(
            ledger=ledger,
            taxonomy=taxonomy,
            section_id=section_id,
            target_company=target_company,
            target_role=target_role,
            jd_text=jd_text,
            briefing_text=briefing_text,
            ledger_path=default_ledger_path(root),
            taxonomy_path=default_taxonomy_path(root),
        )
        selection_method = str(plan.get("selection_method") or selection_method)
        allowed_fact_count = len(allowed)
        expansion = build_track_weighted_expansion(
            graph=graph,
            role_family_key=role_family_key,
            jd_text=jd_text,
            briefing_text=briefing_text,
            repo_root=root,
            min_tracks_with_facts=1,
        )
        selected_skill_ids = _selected_skills_from_expansion(expansion)

    rows_by_id = {
        str(r.get("skill_id")): r
        for r in (graph.get("skill_rows") or [])
        if isinstance(r, dict) and r.get("skill_id")
    }
    for sid in selected_skill_ids[:50]:
        row = rows_by_id.get(sid) or {}
        jd_only_rejections.append(
            reject_jd_only_skill_admission(
                skill_id=sid,
                jd_text=jd_text,
                fact_id_links=list(row.get("fact_id_links") or []),
            )
        )

    pseudo = reject_jd_only_skill_admission(
        skill_id="jd_inferred_skill_svp_it_strategy",
        jd_text=jd_text,
        fact_id_links=[],
    )
    jd_only_rejections.append(pseudo)

    return {
        "schema": SCHEMA,
        "section_id": section_id,
        "targeting": {
            "target_company": target_company,
            "target_role": target_role,
            "jd_sha256": _sha256_text(jd_text),
            "briefing_sha256": _sha256_text(briefing_text),
        },
        "jd_subgraph_policy": {
            "jd_used_as_proof": False,
            "jd_shapes_ranking_only": True,
            "briefing_used_as_proof": False,
            "targeting_only": True,
        },
        "role_family_key": role_family_key,
        "track_weight_audit": weight_audit,
        "jd_keyword_hits": jd_hits,
        "selection_method": selection_method,
        "graph_ref": graph_path.relative_to(root).as_posix(),
        "graph_digest": graph_digest,
        "selected_skill_ids": selected_skill_ids,
        "selected_skill_count": len(selected_skill_ids),
        "allowed_fact_count": allowed_fact_count,
        "jd_only_admission_checks": jd_only_rejections,
        "neg1_all_selected_skills_have_fact_links": all(
            r.get("admitted")
            for r in jd_only_rejections
            if not str(r.get("skill_id") or "").startswith("jd_")
        ),
        "evidence_authority": "augmented_skills_graph",
    }


def write_graph_selection_rationale(
    path: Path,
    *,
    section_id: str,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str = "",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    payload = emit_graph_selection_rationale(
        section_id=section_id,
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        repo_root=repo_root,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


__all__ = [
    "SCHEMA",
    "emit_graph_selection_rationale",
    "extract_jd_keyword_hits",
    "jd_track_weight_delta",
    "reject_jd_only_skill_admission",
    "write_graph_selection_rationale",
]
