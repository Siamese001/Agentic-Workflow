"""SQLite-backed, authority-first C0.3 skill/fact selection for apps_rg.

The JSON graph remains canonical. SQLite is a deterministic projection used to
enumerate direct skill/fact paths. Every bounded direct candidate receives a
pre-target authority decision and a terminal selected/rejected decision.
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
from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    TraversalRecorder,
    build_candidate_decision,
    build_candidate_receipt,
    evaluate_pretarget_authority,
    stable_digest,
)

DEFAULT_MAX_SKILLS_PER_FACT = 6
SCHEMA_VERSION = "c03_sqlite_graph_selection_v2"
SELECTION_POLICY = "sqlite_authority_first_exhaustive_candidates_v2"


class C03GraphSelectionError(RuntimeError):
    """Raised when a required direct graph frontier cannot be selected safely."""


def _confidence_rank(value: str) -> int:
    return {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "BLOCKED": 0}.get(
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


def _query_section_budget(conn: Any, *, section_id: str, role_family_key: str) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT max_metric_reuse, max_fact_family_reuse, required_node_types_json,
               preferred_edge_types_json, forbidden_metric_ids_json,
               preferred_metric_families_json
        FROM section_evidence_budget
        WHERE section_id = ? AND role_family_key IN (?, '*')
        ORDER BY CASE WHEN role_family_key = ? THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (section_id, role_family_key, role_family_key),
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
        "max_metric_reuse": int(row[0] if row[0] is not None else 1),
        "max_fact_family_reuse": int(row[1] if row[1] is not None else 2),
        "required_node_types": _safe_json_list(row[2]),
        "preferred_edge_types": _safe_json_list(row[3]),
        "forbidden_metric_ids": _safe_json_list(row[4]),
        "preferred_metric_families": _safe_json_list(row[5]),
    }


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


def _query_candidates(
    *,
    repo_root: Path,
    db_path: Path,
    section_id: str,
    fact_ids: list[str],
    role_family_key: str,
    run_id: str,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    placeholders = ",".join("?" for _ in fact_ids)
    conn = open_graph_sqlite(repo_root=repo_root, db_path=db_path)
    try:
        meta = load_graph_metadata_row(conn)
        section_budget = _query_section_budget(
            conn, section_id=section_id, role_family_key=role_family_key
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
                CASE WHEN COALESCE(se.allowed, se_any.allowed, 0) = 0 THEN 1 ELSE 0 END
                    AS section_explicitly_blocked,
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
                    WHERE u.run_id = ?
                      AND (u.skill_id = l.skill_id OR u.fact_id = l.fact_id)
                ), 0) AS prior_metric_usage
            FROM skill_fact_links l
            JOIN graph_nodes n ON n.node_id = l.skill_id AND n.node_type = 'skill'
            JOIN c03_skill_selection_features f ON f.skill_id = l.skill_id
            LEFT JOIN section_eligibility se
              ON se.node_id = l.skill_id AND se.section_id = ?
            LEFT JOIN section_eligibility se_any
              ON se_any.node_id = l.skill_id AND se_any.section_id = '*'
            WHERE l.fact_id IN ({placeholders})
            ORDER BY l.fact_id, l.skill_id
            """,
            (run_id or "__NO_CURRENT_RUN__", section_id, *fact_ids),
        ).fetchall()
    finally:
        conn.close()
    return meta, section_budget, [_row_dict(row) for row in rows]


def _proof_strength_raw(candidate: dict[str, Any]) -> float:
    confidence = _confidence_rank(str(candidate.get("confidence") or "")) / 3.0
    path = float(candidate.get("path_score") or 0.0)
    proof = float(candidate.get("proof_strength_score") or 0.0)
    source = min(int(candidate.get("source_fact_count") or 0), 4) * 0.1
    return round(confidence + path + proof + source, 6)


def _target_alignment_score(
    candidate: dict[str, Any], *, role_family_key: str, pillar_hints: set[str]
) -> float:
    weights = _safe_json_object(candidate.get("role_family_weights"))
    role_weight = float(weights.get(role_family_key) or 0.0)
    pillar_match = 1.0 if str(candidate.get("pillar") or "") in pillar_hints else 0.0
    return round(role_weight + pillar_match, 6)


def _authority_for_candidate(candidate: dict[str, Any], *, section_id: str) -> dict[str, Any]:
    source_trace = _safe_json_list(candidate.get("source_trace"))
    source_refs = [candidate.get("fact_id"), *source_trace]
    extra: list[str] = []
    if candidate.get("section_explicitly_blocked") and candidate.get("section_blocked_reason"):
        extra.append(str(candidate["section_blocked_reason"]))
    if not candidate.get("link_external_eligible"):
        extra.append("skill_fact_link_external_eligible_false")
    if int(candidate.get("source_fact_count") or 0) <= 0:
        extra.append("source_fact_count_zero")
    return evaluate_pretarget_authority(
        candidate_id=str(candidate.get("skill_id") or ""),
        candidate_type="leaf_skill",
        section_id=section_id,
        section_allowed=bool(candidate.get("section_allowed")),
        activation_status=str(candidate.get("activation_status") or ""),
        support_level=str(candidate.get("support_level") or candidate.get("link_support_level") or ""),
        external_eligible=bool(candidate.get("external_eligible")),
        claim_eligible=bool(candidate.get("claim_eligibility")),
        source_refs=source_refs,
        path_present=bool(candidate.get("path_signature")),
        extra_reason_codes=extra,
    )


def _rank_fact_candidates(
    candidates: list[dict[str, Any]],
    *,
    section_id: str,
    role_family_key: str,
    pillar_hints: set[str],
    max_skills_per_fact: int,
    metric_counts: Counter[str],
    family_counts: Counter[str],
    fact_counts: Counter[str],
    selected_skill_ids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []

    for raw in candidates:
        candidate = dict(raw)
        authority = _authority_for_candidate(candidate, section_id=section_id)
        candidate["authority"] = authority
        candidate["authority_pass"] = bool(authority["authority_pass"])
        candidate["proof_strength_raw"] = _proof_strength_raw(candidate)
        candidate["target_alignment_score"] = (
            _target_alignment_score(
                candidate,
                role_family_key=role_family_key,
                pillar_hints=pillar_hints,
            )
            if authority["authority_pass"]
            else 0.0
        )
        candidate["base_score"] = round(
            float(candidate["proof_strength_raw"])
            + float(candidate["target_alignment_score"]),
            6,
        )
        if not authority["authority_pass"]:
            candidate["rejection_reason"] = "authority_gate_failed"
            candidate["failed_gate"] = "pretarget_authority"
            rejected.append(candidate)
        elif str(candidate.get("skill_id") or "") in selected_skill_ids:
            candidate["rejection_reason"] = "skill_already_selected_in_section"
            candidate["failed_gate"] = "section_skill_uniqueness"
            rejected.append(candidate)
        else:
            remaining.append(candidate)

    while remaining and len(selected) < max_skills_per_fact:
        scored: list[dict[str, Any]] = []
        for candidate in remaining:
            bucket = str(candidate.get("metric_bucket") or "general_business_outcome")
            family = str(candidate.get("skill_family") or "unclassified")
            fact_id = str(candidate.get("fact_id") or "")
            budget = dict(candidate.get("section_budget") or {})
            max_metric_reuse = int(budget.get("max_metric_reuse") if budget.get("max_metric_reuse") is not None else 1)
            current_run_usage = int(candidate.get("prior_metric_usage") or 0)
            penalties = {
                "repeated_metric_penalty": metric_counts[bucket] * 1.25,
                "repeated_skill_family_penalty": family_counts[family] * 0.75,
                "repeated_fact_penalty": fact_counts[fact_id] * 0.25,
                "prior_metric_usage_penalty": max(
                    0, current_run_usage - max_metric_reuse + 1
                )
                * 1.5,
            }
            item = dict(candidate)
            item["penalties"] = {
                key: round(value, 6) for key, value in penalties.items() if value
            }
            item["score"] = round(
                float(candidate.get("base_score") or 0.0) - sum(penalties.values()),
                6,
            )
            scored.append(item)
        chosen = max(
            scored,
            key=lambda row: (
                float(row.get("score") or 0.0),
                float(row.get("proof_strength_raw") or 0.0),
                str(row.get("skill_id") or ""),
            ),
        )
        selected.append(chosen)
        skill_id = str(chosen.get("skill_id") or "")
        selected_skill_ids.add(skill_id)
        remaining = [row for row in remaining if str(row.get("skill_id") or "") != skill_id]
        metric_counts[str(chosen.get("metric_bucket") or "general_business_outcome")] += 1
        family_counts[str(chosen.get("skill_family") or "unclassified")] += 1
        fact_counts[str(chosen.get("fact_id") or "")] += 1

    for candidate in remaining:
        item = dict(candidate)
        item["rejection_reason"] = "max_skills_per_fact_exceeded"
        item["failed_gate"] = "max_skills_per_fact"
        rejected.append(item)
    return selected, rejected


def _query_sibling_alternatives(
    *,
    repo_root: Path,
    db_path: Path,
    selected_skill_ids: list[str],
    limit_per_skill: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    skill_ids = list(dict.fromkeys(str(value) for value in selected_skill_ids if str(value)))
    if not skill_ids:
        return {}
    placeholders = ",".join("?" for _ in skill_ids)
    conn = open_graph_sqlite(repo_root=repo_root, db_path=db_path)
    try:
        rows = conn.execute(
            f"""
            SELECT sib.node_id, sib.sibling_node_id, n.label, sib.sibling_reason,
                   sib.shared_parent_node_id, sib.shared_edge_type, sib.sibling_score
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
        source = str(row[0] or "")
        if len(out[source]) >= limit_per_skill:
            continue
        out[source].append(
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


def _decision_rows(
    *,
    section_id: str,
    selected_by_fact: dict[str, list[dict[str, Any]]],
    rejected_by_fact: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact_id in sorted(set(selected_by_fact) | set(rejected_by_fact)):
        for candidate in selected_by_fact.get(fact_id, []):
            rows.append(
                build_candidate_decision(
                    section_id=section_id,
                    candidate_id=str(candidate.get("skill_id") or ""),
                    candidate_type="leaf_skill",
                    candidate_path_id=f"fact:{fact_id}/skill:{candidate.get('skill_id')}",
                    decision="selected",
                    reason_codes=["selected_after_authority_and_full_fact_frontier_ranking"],
                    authority=candidate.get("authority") or {},
                    hop_depth=1,
                    parent_id=fact_id,
                    root_id=fact_id,
                    proof_strength_raw=float(candidate.get("proof_strength_raw") or 0.0),
                    target_alignment_score=float(candidate.get("target_alignment_score") or 0.0),
                    ranking_score=float(candidate.get("score") or 0.0),
                    path_signature=str(candidate.get("path_signature") or ""),
                    extra={"metric_bucket": candidate.get("metric_bucket"), "skill_family": candidate.get("skill_family")},
                )
            )
        for candidate in rejected_by_fact.get(fact_id, []):
            reasons = list((candidate.get("authority") or {}).get("reason_codes") or [])
            reasons.append(str(candidate.get("rejection_reason") or "rejected"))
            rows.append(
                build_candidate_decision(
                    section_id=section_id,
                    candidate_id=str(candidate.get("skill_id") or ""),
                    candidate_type="leaf_skill",
                    candidate_path_id=f"fact:{fact_id}/skill:{candidate.get('skill_id')}",
                    decision="rejected",
                    reason_codes=reasons,
                    authority=candidate.get("authority") or {},
                    hop_depth=1,
                    parent_id=fact_id,
                    root_id=fact_id,
                    proof_strength_raw=float(candidate.get("proof_strength_raw") or 0.0),
                    target_alignment_score=float(candidate.get("target_alignment_score") or 0.0),
                    ranking_score=float(candidate.get("score") or candidate.get("base_score") or 0.0),
                    path_signature=str(candidate.get("path_signature") or ""),
                    extra={
                        "failed_gate": candidate.get("failed_gate"),
                        "metric_bucket": candidate.get("metric_bucket"),
                        "skill_family": candidate.get("skill_family"),
                    },
                )
            )
    rows.sort(key=lambda row: str(row.get("candidate_path_id") or ""))
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
    run_id: str = "",
) -> dict[str, Any]:
    """Return deterministic, fail-closed direct candidates and traversal receipts."""
    fact_order = sorted({str(value).strip() for value in selected_fact_ids if str(value).strip()})
    if not fact_order:
        return {
            "schema_version": SCHEMA_VERSION,
            "selection_policy": SELECTION_POLICY,
            "selected_by_fact": {},
            "rejected_by_fact": {},
            "selected_candidates": [],
            "rejected_siblings": [],
            "rejection_receipts": [],
            "candidate_decision_ledger": [],
            "sibling_alternatives_by_skill": {},
            "metric_bucket_counts": {},
            "skill_family_counts": {},
            "missing_fact_frontier_ids": [],
            "candidate_count": 0,
            "selected_skill_count": 0,
            "rejected_sibling_skill_count": 0,
            "sibling_alternative_count": 0,
            "prior_metric_usage_penalty_count": 0,
            "penalty_count": 0,
            "graph_source": "augmented_skills_graph_sqlite",
            "metric_policy_version": POLICY_VERSION,
            "candidate_conservation_pass": True,
        }

    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    # Lazy import prevents the historical materializer -> core package -> L0 ->
    # selector -> context circular import while preserving one public helper.
    from apps_rg.runtime.c03_graph_sqlite_context import require_c03_graph_sqlite

    path = require_c03_graph_sqlite(root, Path(db_path) if db_path else None)
    meta, section_budget, candidates = _query_candidates(
        repo_root=root,
        db_path=path,
        section_id=str(section_id or ""),
        fact_ids=fact_order,
        role_family_key=str(role_family_key or ""),
        run_id=str(run_id or ""),
    )
    for candidate in candidates:
        candidate["section_budget"] = section_budget

    by_fact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_fact[str(candidate.get("fact_id") or "")].append(candidate)

    metric_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    fact_counts: Counter[str] = Counter()
    selected_skill_ids: set[str] = set()
    selected_by_fact: dict[str, list[dict[str, Any]]] = {}
    rejected_by_fact: dict[str, list[dict[str, Any]]] = {}
    for fact_id in fact_order:
        selected, rejected = _rank_fact_candidates(
            by_fact.get(fact_id, []),
            section_id=str(section_id or ""),
            role_family_key=str(role_family_key or ""),
            pillar_hints={str(value) for value in pillar_hints if str(value).strip()},
            max_skills_per_fact=max(1, int(max_skills_per_fact or DEFAULT_MAX_SKILLS_PER_FACT)),
            metric_counts=metric_counts,
            family_counts=family_counts,
            fact_counts=fact_counts,
            selected_skill_ids=selected_skill_ids,
        )
        selected_by_fact[fact_id] = selected
        rejected_by_fact[fact_id] = rejected

    missing_fact_frontier_ids = [fact_id for fact_id in fact_order if not by_fact.get(fact_id)]
    selected_flat = [candidate for rows in selected_by_fact.values() for candidate in rows]
    rejected_flat = [candidate for rows in rejected_by_fact.values() for candidate in rows]
    decisions = _decision_rows(
        section_id=str(section_id or ""),
        selected_by_fact=selected_by_fact,
        rejected_by_fact=rejected_by_fact,
    )

    recorder = TraversalRecorder(section_id=str(section_id or ""), max_hop_depth=1)
    for decision in decisions:
        fact_id = str(decision.get("root_id") or "")
        skill_id = str(decision.get("candidate_id") or "")
        recorder.record(
            event_type="edge_traversed",
            hop_depth=1,
            source_node_id=skill_id,
            target_node_id=fact_id,
            edge_type="skill_supported_by_fact",
            candidate_path_id=str(decision.get("candidate_path_id") or ""),
        )
        authority = decision.get("authority") or {}
        recorder.record(
            event_type="authority_evaluated",
            hop_depth=1,
            source_node_id=skill_id,
            target_node_id=fact_id,
            edge_type="skill_supported_by_fact",
            candidate_path_id=str(decision.get("candidate_path_id") or ""),
            authority_pass=bool(authority.get("authority_pass")),
            reason_codes=authority.get("reason_codes") or [],
        )
        recorder.record(
            event_type="candidate_terminal",
            hop_depth=1,
            source_node_id=skill_id,
            target_node_id=fact_id,
            edge_type="skill_supported_by_fact",
            candidate_path_id=str(decision.get("candidate_path_id") or ""),
            authority_pass=bool(authority.get("authority_pass")),
            decision=str(decision.get("decision") or "rejected"),
            reason_codes=decision.get("reason_codes") or [],
        )
    traversal_receipt = recorder.build_receipt(decisions=decisions)
    traversal_receipt["missing_fact_frontier_ids"] = missing_fact_frontier_ids
    traversal_receipt["frontier_complete"] = not missing_fact_frontier_ids
    traversal_receipt["pass"] = bool(traversal_receipt["pass"] and not missing_fact_frontier_ids)
    traversal_receipt["candidate_conservation"]["pass"] = traversal_receipt["pass"]
    candidate_receipt = build_candidate_receipt(
        section_id=str(section_id or ""), decisions=decisions
    )
    candidate_receipt["missing_fact_frontier_ids"] = missing_fact_frontier_ids
    candidate_receipt["frontier_complete"] = not missing_fact_frontier_ids

    sibling_alternatives_by_skill = _query_sibling_alternatives(
        repo_root=root,
        db_path=path,
        selected_skill_ids=[str(candidate.get("skill_id") or "") for candidate in selected_flat],
    )
    for candidate in selected_flat:
        candidate["sibling_alternatives"] = sibling_alternatives_by_skill.get(
            str(candidate.get("skill_id") or ""), []
        )

    rejection_receipts = [
        {
            "section_id": str(section_id or ""),
            "fact_id": str(row.get("root_id") or ""),
            "candidate_node_id": str(row.get("candidate_id") or ""),
            "candidate_node_type": "skill",
            "rejected_reason": ",".join(str(value) for value in row.get("reason_codes") or []),
            "rejected_at_stage": str(row.get("failed_gate") or "ranking"),
            "competing_selected_node_id": str(
                (selected_by_fact.get(str(row.get("root_id") or "")) or [{}])[0].get("skill_id") or ""
            ),
            "path_signature": str(row.get("path_signature") or ""),
        }
        for row in decisions
        if row.get("decision") == "rejected"
    ]
    authority_rows = [dict(row.get("authority") or {}) for row in decisions]
    authority_receipt = {
        "schema_version": "c03_pretarget_authority_receipt_v1",
        "section_id": str(section_id or ""),
        "candidate_count": len(authority_rows),
        "authority_pass_count": sum(1 for row in authority_rows if row.get("authority_pass")),
        "authority_block_count": sum(1 for row in authority_rows if not row.get("authority_pass")),
        "targeting_consulted_count": sum(1 for row in authority_rows if row.get("targeting_consulted")),
        "authority_before_targeting_pass": all(
            row.get("targeting_consulted") is False
            and row.get("authority_evaluated_before_targeting") is True
            for row in authority_rows
        ),
        "authority_decisions_digest": stable_digest(authority_rows),
    }
    candidate_conservation_pass = bool(
        candidate_receipt["candidate_conservation_pass"]
        and len(decisions) == len(candidates)
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "selection_policy": SELECTION_POLICY,
        "graph_source": "augmented_skills_graph_sqlite",
        "sqlite_db_path": str(path),
        "graph_version": meta.get("graph_version"),
        "graph_hash": meta.get("ledger_hash"),
        "metric_policy_version": POLICY_VERSION,
        "run_id_scope": str(run_id or ""),
        "current_run_usage_only": True,
        "max_skills_per_fact": max_skills_per_fact,
        "source_authority_contract": {
            "schema_version": "c03_source_authority_contract_v1",
            "authority_source": "augmented_skills_graph",
            "graph_digest": meta.get("ledger_hash"),
            "authority_evaluated_before_targeting": True,
            "targeting_inputs_are_non_authority": True,
            "missing_ranked_frontier_fails_closed": True,
        },
        "pretarget_authority_receipt": authority_receipt,
        "selected_by_fact": selected_by_fact,
        "rejected_by_fact": rejected_by_fact,
        "selected_candidates": selected_flat,
        "rejected_siblings": rejected_flat,
        "candidate_decision_ledger": decisions,
        "graph_candidate_receipt": candidate_receipt,
        "graph_traversal_receipt": traversal_receipt,
        "rejection_receipts": rejection_receipts,
        "sibling_alternatives_by_skill": sibling_alternatives_by_skill,
        "sibling_query_limit_per_skill": 5,
        "metric_bucket_counts": dict(sorted(metric_counts.items())),
        "skill_family_counts": dict(sorted(family_counts.items())),
        "missing_fact_frontier_ids": missing_fact_frontier_ids,
        "candidate_count": len(candidates),
        "selected_skill_count": len(selected_flat),
        "rejected_sibling_skill_count": len(rejected_flat),
        "sibling_alternative_count": sum(len(values) for values in sibling_alternatives_by_skill.values()),
        "prior_metric_usage_penalty_count": sum(
            1
            for candidate in selected_flat
            if "prior_metric_usage_penalty" in dict(candidate.get("penalties") or {})
        ),
        "penalty_count": sum(1 for candidate in selected_flat if candidate.get("penalties")),
        "authority_block_count": authority_receipt["authority_block_count"],
        "candidate_conservation_pass": candidate_conservation_pass,
        "selection_contract_pass": bool(
            candidate_conservation_pass
            and authority_receipt["authority_before_targeting_pass"]
            and not missing_fact_frontier_ids
            and selected_flat
        ),
    }


__all__ = [
    "C03GraphSelectionError",
    "DEFAULT_MAX_SKILLS_PER_FACT",
    "SCHEMA_VERSION",
    "SELECTION_POLICY",
    "select_c03_sqlite_graph_candidates",
]
