"""SQLite-backed C0.3 skill/fact selection for apps_rg.

The canonical graph source remains the JSON ledger. This module queries the
generated SQLite projection so C0.3 can rank direct skill/fact bindings,
penalize repeated metric/family neighborhoods, and receipt rejected siblings
deterministically.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    load_graph_metadata_row,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_metric_heterogeneity_policy import POLICY_VERSION
from apps_rg.runtime.c03_graph_sqlite_context import ensure_c03_graph_sqlite

DEFAULT_MAX_SKILLS_PER_FACT = 6
SCHEMA_VERSION = "c03_sqlite_graph_selection_v1"


def _confidence_rank(value: str) -> int:
    return {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "BLOCKED": -2}.get(
        str(value or "").upper(), 0
    )


def _safe_json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    try:
        loaded = json.loads(str(value or "{}"))
    except json.JSONDecodeError:
        return {}
    return dict(loaded) if isinstance(loaded, dict) else {}


def _safe_json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return list(value)
    try:
        loaded = json.loads(str(value or "[]"))
    except json.JSONDecodeError:
        return []
    return list(loaded) if isinstance(loaded, list) else []


def _candidate_base_score(
    row: dict[str, Any],
    *,
    role_family_key: str,
    pillar_hints: set[str],
) -> float:
    weights = _safe_json_object(row.get("role_family_weights"))
    role_weight = float(weights.get(role_family_key) or 0.0)
    pillar_match = 1.0 if str(row.get("pillar") or "") in pillar_hints else 0.0
    prior_usage = float(row.get("prior_metric_usage") or 0.0)
    score = (
        (10.0 if row.get("claim_eligibility") else 0.0)
        + (4.0 if row.get("external_eligible") else 0.0)
        + (2.0 if row.get("section_allowed") else 0.0)
        + (_confidence_rank(str(row.get("confidence") or "")) * 1.5)
        + (pillar_match * 2.5)
        + role_weight
        + min(int(row.get("source_fact_count") or 0), 3) * 0.25
        - min(prior_usage, 5.0)
    )
    return round(
        score,
        4,
    )


def _row_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    return {
        "fact_id": str(row[0] or ""),
        "skill_id": str(row[1] or ""),
        "skill_label": str(row[2] or ""),
        "claim_eligibility": bool(row[3]),
        "link_external_eligible": bool(row[4]),
        "link_support_level": str(row[5] or ""),
        "pillar": str(row[6] or ""),
        "subpillar": str(row[7] or ""),
        "domain_id": str(row[8] or ""),
        "skill_family": str(row[9] or "unclassified"),
        "metric_bucket": str(row[10] or "general_business_outcome"),
        "role_family_weights": str(row[11] or "{}"),
        "source_fact_count": int(row[12] or 0),
        "confidence": str(row[13] or ""),
        "activation_status": str(row[14] or ""),
        "support_level": str(row[15] or ""),
        "external_eligible": bool(row[16]),
        "source_trace": str(row[17] or "[]"),
        "section_allowed": bool(row[18]),
        "section_explicitly_blocked": bool(row[19]),
        "section_blocked_reason": str(row[20] or ""),
        "path_signature": str(row[21] or ""),
        "path_score": float(row[22] or 0.0),
        "proof_strength_score": float(row[23] or 0.0),
        "prior_metric_usage": int(row[24] or 0),
    }


def _query_section_budget(conn: Any, *, section_id: str, role_family_key: str) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT max_metric_reuse, max_fact_family_reuse, required_node_types_json,
               preferred_edge_types_json, forbidden_metric_ids_json,
               preferred_metric_families_json
        FROM section_evidence_budget
        WHERE section_id = ? AND role_family_key = ?
        """,
        (section_id, role_family_key),
    ).fetchone()
    if row is None:
        return {
            "max_metric_reuse": 1,
            "max_fact_family_reuse": 2,
            "required_node_types": ["skill", "fact"],
            "preferred_edge_types": ["skill_supported_by_fact"],
            "forbidden_metric_ids": [],
            "preferred_metric_families": [],
        }
    return {
        "max_metric_reuse": int(row[0] or 1),
        "max_fact_family_reuse": int(row[1] or 2),
        "required_node_types": _safe_json_list(row[2]),
        "preferred_edge_types": _safe_json_list(row[3]),
        "forbidden_metric_ids": _safe_json_list(row[4]),
        "preferred_metric_families": _safe_json_list(row[5]),
    }


def _query_candidates(
    *,
    repo_root: Path,
    db_path: Path,
    section_id: str,
    fact_ids: list[str],
    role_family_key: str,
    pillar_hints: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    placeholders = ",".join("?" for _ in fact_ids)
    conn = open_graph_sqlite(repo_root=repo_root, db_path=db_path)
    try:
        meta = load_graph_metadata_row(conn)
        section_budget = _query_section_budget(
            conn,
            section_id=section_id,
            role_family_key=role_family_key,
        )
        rows = conn.execute(
            f"""
            SELECT
                l.fact_id,
                l.skill_id,
                n.label,
                l.claim_eligibility,
                l.external_eligible,
                l.support_level,
                f.pillar,
                f.subpillar,
                f.domain_id,
                f.skill_family,
                f.metric_bucket,
                f.role_family_weights,
                f.source_fact_count,
                f.confidence,
                f.activation_status,
                f.support_level,
                f.external_eligible,
                f.source_trace,
                COALESCE(se.allowed, se_any.allowed, 0) AS section_allowed,
                CASE WHEN se.allowed = 0 THEN 1 ELSE 0 END AS section_explicitly_blocked,
                COALESCE(se.blocked_reason, se_any.blocked_reason, '') AS section_blocked_reason,
                COALESCE((
                    SELECT p.path_signature FROM graph_paths p
                    WHERE p.start_node_id = l.skill_id AND p.end_node_id = l.fact_id
                    ORDER BY p.path_depth ASC, p.path_score DESC, p.path_id
                    LIMIT 1
                ), '') AS path_signature,
                COALESCE((
                    SELECT p.path_score FROM graph_paths p
                    WHERE p.start_node_id = l.skill_id AND p.end_node_id = l.fact_id
                    ORDER BY p.path_depth ASC, p.path_score DESC, p.path_id
                    LIMIT 1
                ), 0.0) AS path_score,
                COALESCE((
                    SELECT p.proof_strength_score FROM graph_paths p
                    WHERE p.start_node_id = l.skill_id AND p.end_node_id = l.fact_id
                    ORDER BY p.path_depth ASC, p.path_score DESC, p.path_id
                    LIMIT 1
                ), 0.0) AS proof_strength_score,
                COALESCE((
                    SELECT SUM(u.usage_count) FROM resume_metric_usage u
                    WHERE u.skill_id = l.skill_id
                       OR u.fact_id = l.fact_id
                       OR (u.role_family_key = ? AND u.resume_section = ?)
                ), 0) AS prior_metric_usage
            FROM skill_fact_links l
            JOIN graph_nodes n ON n.node_id = l.skill_id AND n.node_type = 'skill'
            JOIN c03_skill_selection_features f ON f.skill_id = l.skill_id
            LEFT JOIN section_eligibility se
              ON se.node_id = l.skill_id AND se.section_id = ?
            LEFT JOIN section_eligibility se_any
              ON se_any.node_id = l.skill_id AND se_any.section_id = '*'
            WHERE l.fact_id IN ({placeholders})
            ORDER BY l.fact_id, l.claim_eligibility DESC, f.external_eligible DESC,
                     f.confidence DESC, f.metric_bucket, l.skill_id
            """,
            (role_family_key, section_id, section_id, *fact_ids),
        ).fetchall()
    finally:
        conn.close()

    candidates = [_row_dict(row) for row in rows]
    for candidate in candidates:
        candidate["section_budget"] = section_budget
        candidate["base_score"] = _candidate_base_score(
            candidate,
            role_family_key=role_family_key,
            pillar_hints=pillar_hints,
        )
    return meta, candidates


def _rank_fact_candidates(
    candidates: list[dict[str, Any]],
    *,
    max_skills_per_fact: int,
    metric_counts: Counter[str],
    family_counts: Counter[str],
    fact_counts: Counter[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    remaining = [dict(c) for c in candidates]

    for candidate in list(remaining):
        if candidate.get("section_explicitly_blocked"):
            candidate["rejection_reason"] = candidate.get("section_blocked_reason") or "section_blocked"
            candidate["failed_gate"] = "section_eligibility"
            rejected.append(candidate)
            remaining.remove(candidate)
        elif not candidate.get("claim_eligibility"):
            candidate["rejection_reason"] = "not_claim_eligible"
            candidate["failed_gate"] = "claim_eligibility"
            rejected.append(candidate)
            remaining.remove(candidate)

    while remaining and len(selected) < max_skills_per_fact:
        scored: list[dict[str, Any]] = []
        for candidate in remaining:
            bucket = str(candidate.get("metric_bucket") or "general_business_outcome")
            family = str(candidate.get("skill_family") or "unclassified")
            fact_id = str(candidate.get("fact_id") or "")
            budget = dict(candidate.get("section_budget") or {})
            max_metric_reuse = int(budget.get("max_metric_reuse") or 1)
            prior_usage = int(candidate.get("prior_metric_usage") or 0)
            penalties = {
                "repeated_metric_penalty": metric_counts[bucket] * 1.25,
                "repeated_skill_family_penalty": family_counts[family] * 0.75,
                "repeated_fact_penalty": fact_counts[fact_id] * 0.25,
                "prior_metric_usage_penalty": max(0, prior_usage - max_metric_reuse + 1)
                * 1.5,
            }
            graph_bonus = float(candidate.get("path_score") or 0.0) + float(
                candidate.get("proof_strength_score") or 0.0
            )
            final_score = (
                float(candidate.get("base_score") or 0.0)
                + graph_bonus
                - sum(penalties.values())
            )
            item = dict(candidate)
            item["score"] = round(final_score, 4)
            item["penalties"] = {k: round(v, 4) for k, v in penalties.items() if v}
            scored.append(item)
        chosen = max(scored, key=lambda c: (float(c["score"]), float(c["base_score"]), c["skill_id"]))
        selected.append(chosen)
        remaining = [c for c in remaining if c["skill_id"] != chosen["skill_id"]]
        metric_counts[str(chosen.get("metric_bucket") or "general_business_outcome")] += 1
        family_counts[str(chosen.get("skill_family") or "unclassified")] += 1
        fact_counts[str(chosen.get("fact_id") or "")] += 1

    for candidate in remaining:
        bucket = str(candidate.get("metric_bucket") or "general_business_outcome")
        family = str(candidate.get("skill_family") or "unclassified")
        if metric_counts[bucket]:
            reason = "repeated_metric_penalty"
            gate = "metric_novelty"
        elif family_counts[family]:
            reason = "repeated_skill_family_penalty"
            gate = "skill_family_novelty"
        elif int(candidate.get("prior_metric_usage") or 0):
            reason = "prior_metric_usage_penalty"
            gate = "metric_usage_memory"
        else:
            reason = "max_skills_per_fact_exceeded"
            gate = "max_skills_per_fact"
        item = dict(candidate)
        item["rejection_reason"] = reason
        item["failed_gate"] = gate
        rejected.append(item)

    return selected, rejected


def _query_sibling_alternatives(
    *,
    repo_root: Path,
    db_path: Path,
    selected_skill_ids: list[str],
    limit_per_skill: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    skill_ids = list(dict.fromkeys(str(sid) for sid in selected_skill_ids if str(sid)))
    if not skill_ids:
        return {}
    placeholders = ",".join("?" for _ in skill_ids)
    conn = open_graph_sqlite(repo_root=repo_root, db_path=db_path)
    try:
        rows = conn.execute(
            f"""
            SELECT
                sib.node_id,
                sib.sibling_node_id,
                n.label,
                sib.sibling_reason,
                sib.shared_parent_node_id,
                sib.shared_edge_type,
                sib.sibling_score
            FROM graph_sibling_links sib
            JOIN graph_nodes n
              ON n.node_id = sib.sibling_node_id AND n.node_type = 'skill'
            WHERE sib.node_id IN ({placeholders})
              AND n.external_eligible = 1
            ORDER BY sib.node_id, sib.sibling_score DESC, sib.sibling_node_id
            """,
            tuple(skill_ids),
        ).fetchall()
    finally:
        conn.close()

    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        sid = str(row[0] or "")
        if len(out[sid]) >= limit_per_skill:
            continue
        out[sid].append(
            {
                "skill_id": str(row[1] or ""),
                "skill_label": str(row[2] or ""),
                "sibling_reason": str(row[3] or ""),
                "shared_parent_node_id": str(row[4] or ""),
                "shared_edge_type": str(row[5] or ""),
                "sibling_score": float(row[6] or 0.0),
            }
        )
    return dict(out)


def _build_rejection_receipts(
    *,
    selected_by_fact: dict[str, list[dict[str, Any]]],
    rejected_by_fact: dict[str, list[dict[str, Any]]],
    section_id: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact_id, rejected in rejected_by_fact.items():
        competing = ""
        if selected_by_fact.get(fact_id):
            competing = str(selected_by_fact[fact_id][0].get("skill_id") or "")
        for candidate in rejected:
            rows.append(
                {
                    "section_id": section_id,
                    "fact_id": fact_id,
                    "candidate_node_id": str(candidate.get("skill_id") or ""),
                    "candidate_node_type": "skill",
                    "rejected_reason": str(candidate.get("rejection_reason") or ""),
                    "rejected_at_stage": str(candidate.get("failed_gate") or ""),
                    "competing_selected_node_id": competing,
                    "path_signature": str(candidate.get("path_signature") or ""),
                }
            )
    return rows


def select_c03_sqlite_graph_candidates(
    *,
    section_id: str,
    selected_fact_ids: list[str],
    role_family_key: str,
    pillar_hints: list[str] | tuple[str, ...] = (),
    repo_root: Path | None = None,
    db_path: Path | None = None,
    max_skills_per_fact: int = DEFAULT_MAX_SKILLS_PER_FACT,
) -> dict[str, Any]:
    """Return deterministic SQLite-ranked C0.3 candidates and rejected siblings."""
    fact_order = [str(fid).strip() for fid in selected_fact_ids if str(fid).strip()]
    if not fact_order:
        return {
            "schema_version": SCHEMA_VERSION,
            "selection_policy": "sqlite_ranked_metric_novelty_v1",
            "selected_by_fact": {},
            "rejected_by_fact": {},
            "selected_candidates": [],
            "rejected_siblings": [],
            "rejection_receipts": [],
            "sibling_alternatives_by_skill": {},
            "metric_bucket_counts": {},
            "rejected_sibling_skill_count": 0,
            "sibling_alternative_count": 0,
            "prior_metric_usage_penalty_count": 0,
            "candidate_count": 0,
            "graph_source": "augmented_skills_graph_sqlite",
            "metric_policy_version": POLICY_VERSION,
        }

    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    path = ensure_c03_graph_sqlite(root, Path(db_path) if db_path else None)
    unique_facts = list(dict.fromkeys(fact_order))
    meta, candidates = _query_candidates(
        repo_root=root,
        db_path=path,
        section_id=str(section_id or ""),
        fact_ids=unique_facts,
        role_family_key=str(role_family_key or ""),
        pillar_hints={str(p) for p in pillar_hints if str(p).strip()},
    )

    by_fact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_fact[str(candidate.get("fact_id") or "")].append(candidate)

    metric_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    fact_counts: Counter[str] = Counter()
    selected_by_fact: dict[str, list[dict[str, Any]]] = {}
    rejected_by_fact: dict[str, list[dict[str, Any]]] = {}

    for fact_id in fact_order:
        selected, rejected = _rank_fact_candidates(
            by_fact.get(fact_id, []),
            max_skills_per_fact=max(1, int(max_skills_per_fact or DEFAULT_MAX_SKILLS_PER_FACT)),
            metric_counts=metric_counts,
            family_counts=family_counts,
            fact_counts=fact_counts,
        )
        selected_by_fact[fact_id] = selected
        rejected_by_fact[fact_id] = rejected

    selected_flat = [c for rows in selected_by_fact.values() for c in rows]
    rejected_flat = [c for rows in rejected_by_fact.values() for c in rows]
    sibling_alternatives_by_skill = _query_sibling_alternatives(
        repo_root=root,
        db_path=path,
        selected_skill_ids=[str(c.get("skill_id") or "") for c in selected_flat],
    )
    for candidate in selected_flat:
        candidate["sibling_alternatives"] = sibling_alternatives_by_skill.get(
            str(candidate.get("skill_id") or ""),
            [],
        )
    rejection_receipts = _build_rejection_receipts(
        selected_by_fact=selected_by_fact,
        rejected_by_fact=rejected_by_fact,
        section_id=str(section_id or ""),
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "selection_policy": "sqlite_ranked_metric_novelty_v1",
        "graph_source": "augmented_skills_graph_sqlite",
        "sqlite_db_path": str(path),
        "graph_version": meta.get("graph_version"),
        "graph_hash": meta.get("ledger_hash"),
        "metric_policy_version": POLICY_VERSION,
        "max_skills_per_fact": max_skills_per_fact,
        "selected_by_fact": selected_by_fact,
        "rejected_by_fact": rejected_by_fact,
        "selected_candidates": selected_flat,
        "rejected_siblings": rejected_flat,
        "rejection_receipts": rejection_receipts,
        "sibling_alternatives_by_skill": sibling_alternatives_by_skill,
        "metric_bucket_counts": dict(sorted(metric_counts.items())),
        "skill_family_counts": dict(sorted(family_counts.items())),
        "candidate_count": len(candidates),
        "selected_skill_count": len(selected_flat),
        "rejected_sibling_skill_count": len(rejected_flat),
        "sibling_alternative_count": sum(
            len(v) for v in sibling_alternatives_by_skill.values()
        ),
        "prior_metric_usage_penalty_count": sum(
            1
            for c in selected_flat
            if "prior_metric_usage_penalty" in dict(c.get("penalties") or {})
        ),
        "penalty_count": sum(1 for c in selected_flat if c.get("penalties")),
    }


__all__ = [
    "DEFAULT_MAX_SKILLS_PER_FACT",
    "SCHEMA_VERSION",
    "select_c03_sqlite_graph_candidates",
]
