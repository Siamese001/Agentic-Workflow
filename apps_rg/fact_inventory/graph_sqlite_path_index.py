"""Deterministic graph-index projections for the augmented skills SQLite DB.

The JSON ledger remains canonical. This module builds generated helper rows
from materialized graph nodes/edges so SQLite can answer bounded path,
neighborhood, sibling, section-budget, and diagnostic-style graph queries.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

GRAPH_INDEX_SCHEMA_VERSION = "graph_sqlite_path_index_v1"
DEFAULT_MAX_DEPTH = 4
DEFAULT_MAX_EDGES_PER_NODE = 24

GRAPH_INDEX_OBJECTS = (
    "graph_edges_reverse",
    "graph_paths",
    "graph_neighborhoods",
    "graph_sibling_links",
    "resume_metric_usage",
    "section_evidence_budget",
    "graph_selection_rejections",
)


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _hash_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:24]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _node_type(node_by_id: dict[str, dict[str, Any]], node_id: str) -> str:
    return str((node_by_id.get(node_id) or {}).get("node_type") or "")


def _edge_weight(edge: dict[str, Any]) -> float:
    try:
        return float(edge.get("weight") or 1.0)
    except (TypeError, ValueError):
        return 1.0


def _path_scores(
    *,
    node_by_id: dict[str, dict[str, Any]],
    edge_path: list[dict[str, Any]],
    node_path: list[str],
) -> tuple[float, float, float]:
    depth = max(1, len(edge_path))
    total_weight = sum(_edge_weight(e) for e in edge_path)
    path_score = round(total_weight / depth, 4)
    edge_type_count = len({str(e.get("edge_type") or "") for e in edge_path})
    novelty_score = round(edge_type_count / depth, 4)
    proof_strength = 0.0
    if any(_node_type(node_by_id, nid) == "fact" for nid in node_path):
        proof_strength += 1.0
    if any(_node_type(node_by_id, nid) == "metric_outcome" for nid in node_path):
        proof_strength += 0.75
    if any(str(e.get("external_claim_policy") or "") for e in edge_path):
        proof_strength += 0.25
    return path_score, novelty_score, round(proof_strength, 4)


def _build_path_rows(
    *,
    node_by_id: dict[str, dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    created_at: str,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> list[dict[str, Any]]:
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edge_rows:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        if src in node_by_id and tgt in node_by_id:
            adjacency[src].append(edge)
    for edges in adjacency.values():
        edges.sort(
            key=lambda e: (
                str(e.get("edge_type") or ""),
                str(e.get("target_node_id") or ""),
                str(e.get("edge_id") or ""),
            )
        )

    start_types = {
        "role_family",
        "career_track",
        "pillar",
        "capability_domain",
        "skill",
        "fact",
        "metric_outcome",
        "employment",
    }
    rows: dict[str, dict[str, Any]] = {}

    def walk(start: str, current: str, node_path: list[str], edge_path: list[dict[str, Any]]) -> None:
        if edge_path:
            edge_ids = [str(e.get("edge_id") or "") for e in edge_path]
            edge_types = [str(e.get("edge_type") or "") for e in edge_path]
            signature = "->".join(node_path)
            proof_fact_ids = [nid for nid in node_path if _node_type(node_by_id, nid) == "fact"]
            metric_ids = [nid for nid in node_path if _node_type(node_by_id, nid) == "metric_outcome"]
            section_ids = [nid for nid in node_path if _node_type(node_by_id, nid) == "section"]
            path_score, novelty_score, proof_strength = _path_scores(
                node_by_id=node_by_id,
                edge_path=edge_path,
                node_path=node_path,
            )
            path_id = _hash_id("path", signature + "|" + "|".join(edge_ids))
            rows[path_id] = {
                "path_id": path_id,
                "start_node_id": start,
                "end_node_id": current,
                "path_depth": len(edge_path),
                "path_signature": signature,
                "node_path_json": _json(node_path),
                "edge_path_json": _json(edge_ids),
                "edge_types_json": _json(edge_types),
                "proof_fact_ids_json": _json(proof_fact_ids),
                "metric_ids_json": _json(metric_ids),
                "section_ids_json": _json(section_ids),
                "path_score": path_score,
                "novelty_score": novelty_score,
                "proof_strength_score": proof_strength,
                "created_at": created_at,
            }
        if len(edge_path) >= max_depth:
            return
        for edge in adjacency.get(current, [])[:DEFAULT_MAX_EDGES_PER_NODE]:
            nxt = str(edge.get("target_node_id") or "")
            if nxt in node_path:
                continue
            walk(start, nxt, [*node_path, nxt], [*edge_path, edge])

    for node_id, node in sorted(node_by_id.items()):
        if str(node.get("node_type") or "") in start_types:
            walk(node_id, node_id, [node_id], [])
    return sorted(rows.values(), key=lambda r: (r["start_node_id"], r["path_depth"], r["end_node_id"]))


def _build_neighborhood_rows(path_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: dict[tuple[str, str, int], dict[str, Any]] = {}
    for path in path_rows:
        key = (
            str(path["start_node_id"]),
            str(path["end_node_id"]),
            int(path["path_depth"]),
        )
        row = {
            "center_node_id": key[0],
            "neighbor_node_id": key[1],
            "distance": key[2],
            "connecting_path_json": str(path["node_path_json"]),
            "edge_types_json": str(path["edge_types_json"]),
            "relationship_summary": (
                f"distance={path['path_depth']}; edge_types="
                f"{','.join(json.loads(str(path['edge_types_json'])))}"
            ),
            "neighbor_score": round(
                float(path.get("path_score") or 0.0)
                + float(path.get("novelty_score") or 0.0)
                + float(path.get("proof_strength_score") or 0.0),
                4,
            ),
        }
        prior = chosen.get(key)
        if prior is None or row["neighbor_score"] > prior["neighbor_score"]:
            chosen[key] = row
    return sorted(chosen.values(), key=lambda r: (r["center_node_id"], r["distance"], r["neighbor_node_id"]))


def build_graph_neighborhoods(path_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return generated graph_neighborhoods rows from path rows."""
    return _build_neighborhood_rows(path_rows)


def _upsert_sibling(
    rows: dict[tuple[str, str], dict[str, Any]],
    *,
    node_id: str,
    sibling_node_id: str,
    sibling_reason: str,
    shared_parent_node_id: str,
    shared_edge_type: str,
    sibling_score: float,
) -> None:
    if not node_id or not sibling_node_id or node_id == sibling_node_id:
        return
    key = (node_id, sibling_node_id)
    row = {
        "node_id": node_id,
        "sibling_node_id": sibling_node_id,
        "sibling_reason": sibling_reason,
        "shared_parent_node_id": shared_parent_node_id,
        "shared_edge_type": shared_edge_type,
        "sibling_score": round(sibling_score, 4),
    }
    prior = rows.get(key)
    if prior is None or row["sibling_score"] > float(prior["sibling_score"]):
        rows[key] = row


def _build_sibling_rows(
    *,
    node_by_id: dict[str, dict[str, Any]],
    edge_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    parent_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    fact_groups: dict[tuple[str, str], list[str]] = defaultdict(list)

    for edge in edge_rows:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        etype = str(edge.get("edge_type") or "")
        if _node_type(node_by_id, tgt) == "skill" and _node_type(node_by_id, src) != "skill":
            parent_groups[(src, etype)].append(tgt)
        if _node_type(node_by_id, src) == "skill" and _node_type(node_by_id, tgt) == "fact":
            fact_groups[(tgt, etype)].append(src)

    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for (parent, etype), skills in sorted(parent_groups.items()):
        uniq = sorted(set(skills))
        for skill in uniq:
            for sibling in uniq:
                _upsert_sibling(
                    rows,
                    node_id=skill,
                    sibling_node_id=sibling,
                    sibling_reason=f"shared_parent:{etype}",
                    shared_parent_node_id=parent,
                    shared_edge_type=etype,
                    sibling_score=1.0,
                )
    for (fact_id, etype), skills in sorted(fact_groups.items()):
        uniq = sorted(set(skills))
        for skill in uniq:
            for sibling in uniq:
                _upsert_sibling(
                    rows,
                    node_id=skill,
                    sibling_node_id=sibling,
                    sibling_reason="shared_fact",
                    shared_parent_node_id=fact_id,
                    shared_edge_type=etype,
                    sibling_score=1.5,
                )
    return sorted(rows.values(), key=lambda r: (r["node_id"], -float(r["sibling_score"]), r["sibling_node_id"]))


def build_graph_sibling_links(
    *,
    node_rows: list[dict[str, Any]],
    edge_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return generated sibling links from shared graph parents/facts."""
    node_by_id = {str(row.get("node_id") or ""): row for row in node_rows if str(row.get("node_id") or "")}
    return _build_sibling_rows(node_by_id=node_by_id, edge_rows=edge_rows)


def _section_budget_defaults(section_id: str) -> dict[str, Any]:
    normalized = str(section_id or "").lower()
    if normalized == "executive_summary":
        return {
            "max_metric_reuse": 1,
            "max_fact_family_reuse": 2,
            "required_node_types_json": ["skill", "fact"],
            "preferred_edge_types_json": ["skill_supported_by_fact", "skill_allowed_in_section"],
            "preferred_metric_families_json": ["risk_governance", "platform_scale", "business_outcome"],
        }
    if "competenc" in normalized:
        return {
            "max_metric_reuse": 1,
            "max_fact_family_reuse": 3,
            "required_node_types_json": ["skill"],
            "preferred_edge_types_json": ["capability_domain_contains_skill", "pillar_contains_capability_domain"],
            "preferred_metric_families_json": ["breadth", "platform_scale"],
        }
    if "technical" in normalized or "architecture" in normalized:
        return {
            "max_metric_reuse": 1,
            "max_fact_family_reuse": 2,
            "required_node_types_json": ["skill", "fact", "metric_outcome"],
            "preferred_edge_types_json": ["skill_supported_by_fact", "metric_outcome_section_eligible"],
            "preferred_metric_families_json": ["platform_scale", "risk_governance"],
        }
    return {
        "max_metric_reuse": 1,
        "max_fact_family_reuse": 2,
        "required_node_types_json": ["skill", "fact"],
        "preferred_edge_types_json": ["skill_supported_by_fact", "skill_allowed_in_section"],
        "preferred_metric_families_json": [],
    }


def _build_section_budget_rows(
    *,
    node_by_id: dict[str, dict[str, Any]],
    section_rows: list[dict[str, Any]],
    role_family_projection_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sections = {
        str(nid)
        for nid, row in node_by_id.items()
        if str(row.get("node_type") or "") == "section"
    }
    sections.update(str(r.get("section_id") or "") for r in section_rows if str(r.get("section_id") or ""))
    role_families = [
        str(r.get("projection_role_family_key") or r.get("role_family_id") or "")
        for r in role_family_projection_rows
    ]
    role_families = sorted({rf for rf in role_families if rf})
    rows: list[dict[str, Any]] = []
    for section in sorted(sections):
        defaults = _section_budget_defaults(section)
        for role_family in role_families:
            rows.append(
                {
                    "section_id": section,
                    "role_family_key": role_family,
                    "max_metric_reuse": int(defaults["max_metric_reuse"]),
                    "max_fact_family_reuse": int(defaults["max_fact_family_reuse"]),
                    "required_node_types_json": _json(defaults["required_node_types_json"]),
                    "preferred_edge_types_json": _json(defaults["preferred_edge_types_json"]),
                    "forbidden_metric_ids_json": "[]",
                    "preferred_metric_families_json": _json(defaults["preferred_metric_families_json"]),
                }
            )
    return rows


def build_graph_index_rows(
    *,
    node_rows: list[dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    section_rows: list[dict[str, Any]],
    role_family_projection_rows: list[dict[str, Any]],
    created_at: str,
) -> dict[str, list[dict[str, Any]]]:
    """Build deterministic graph-index helper rows from materialized rows."""
    node_by_id = {str(row.get("node_id") or ""): row for row in node_rows if str(row.get("node_id") or "")}
    normalized_edges = [
        dict(row)
        for row in edge_rows
        if str(row.get("source_node_id") or "") and str(row.get("target_node_id") or "")
    ]
    path_rows = _build_path_rows(
        node_by_id=node_by_id,
        edge_rows=normalized_edges,
        created_at=created_at,
    )
    return {
        "graph_paths": path_rows,
        "graph_neighborhoods": build_graph_neighborhoods(path_rows),
        "graph_sibling_links": build_graph_sibling_links(
            node_rows=list(node_by_id.values()),
            edge_rows=normalized_edges,
        ),
        "section_evidence_budget": _build_section_budget_rows(
            node_by_id=node_by_id,
            section_rows=section_rows,
            role_family_projection_rows=role_family_projection_rows,
        ),
    }


def build_reverse_edge_view(conn: sqlite3.Connection) -> None:
    """Create the reverse traversal view without duplicating physical edge rows."""
    conn.execute(
        """
        CREATE VIEW IF NOT EXISTS graph_edges_reverse AS
        SELECT
            edge_id,
            target_node_id AS source_node_id,
            source_node_id AS target_node_id,
            edge_type || '_reverse' AS edge_type,
            edge_family,
            weight,
            confidence,
            evidence_status,
            section_fit,
            source_authority,
            rationale,
            projection_behavior,
            external_claim_policy,
            validation_status,
            edge_note,
            operator_note,
            business_story,
            technical_story
        FROM graph_edges
        """
    )


def _fetch_rows(conn: sqlite3.Connection, query: str) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(query).fetchall()
    return [dict(row) for row in rows]


def materialize_graph_path_index(conn: sqlite3.Connection, *, created_at: str | None = None) -> dict[str, int]:
    """Rebuild generated path/neighborhood/sibling/budget rows from graph tables."""
    ts = created_at or _utc_now()
    build_reverse_edge_view(conn)
    node_rows = _fetch_rows(conn, "SELECT * FROM graph_nodes ORDER BY node_id")
    edge_rows = _fetch_rows(conn, "SELECT * FROM graph_edges ORDER BY edge_id")
    section_rows = _fetch_rows(conn, "SELECT * FROM section_eligibility ORDER BY node_id, section_id")
    role_rows = _fetch_rows(conn, "SELECT * FROM role_family_projection ORDER BY role_family_id")
    rows = build_graph_index_rows(
        node_rows=node_rows,
        edge_rows=edge_rows,
        section_rows=section_rows,
        role_family_projection_rows=role_rows,
        created_at=ts,
    )
    conn.execute("DELETE FROM graph_paths")
    conn.execute("DELETE FROM graph_neighborhoods")
    conn.execute("DELETE FROM graph_sibling_links")
    conn.execute("DELETE FROM section_evidence_budget")
    conn.executemany(
        """
        INSERT INTO graph_paths (
            path_id, start_node_id, end_node_id, path_depth, path_signature,
            node_path_json, edge_path_json, edge_types_json, proof_fact_ids_json,
            metric_ids_json, section_ids_json, path_score, novelty_score,
            proof_strength_score, created_at
        ) VALUES (
            :path_id, :start_node_id, :end_node_id, :path_depth, :path_signature,
            :node_path_json, :edge_path_json, :edge_types_json, :proof_fact_ids_json,
            :metric_ids_json, :section_ids_json, :path_score, :novelty_score,
            :proof_strength_score, :created_at
        )
        """,
        rows["graph_paths"],
    )
    conn.executemany(
        """
        INSERT INTO graph_neighborhoods (
            center_node_id, neighbor_node_id, distance, connecting_path_json,
            edge_types_json, relationship_summary, neighbor_score
        ) VALUES (
            :center_node_id, :neighbor_node_id, :distance, :connecting_path_json,
            :edge_types_json, :relationship_summary, :neighbor_score
        )
        """,
        rows["graph_neighborhoods"],
    )
    conn.executemany(
        """
        INSERT INTO graph_sibling_links (
            node_id, sibling_node_id, sibling_reason, shared_parent_node_id,
            shared_edge_type, sibling_score
        ) VALUES (
            :node_id, :sibling_node_id, :sibling_reason, :shared_parent_node_id,
            :shared_edge_type, :sibling_score
        )
        """,
        rows["graph_sibling_links"],
    )
    conn.executemany(
        """
        INSERT INTO section_evidence_budget (
            section_id, role_family_key, max_metric_reuse, max_fact_family_reuse,
            required_node_types_json, preferred_edge_types_json,
            forbidden_metric_ids_json, preferred_metric_families_json
        ) VALUES (
            :section_id, :role_family_key, :max_metric_reuse, :max_fact_family_reuse,
            :required_node_types_json, :preferred_edge_types_json,
            :forbidden_metric_ids_json, :preferred_metric_families_json
        )
        """,
        rows["section_evidence_budget"],
    )
    return {
        "graph_path_count": len(rows["graph_paths"]),
        "graph_neighborhood_count": len(rows["graph_neighborhoods"]),
        "graph_sibling_link_count": len(rows["graph_sibling_links"]),
        "section_evidence_budget_count": len(rows["section_evidence_budget"]),
    }


def record_resume_metric_usage(
    conn: sqlite3.Connection,
    *,
    run_id: str,
    resume_section: str,
    metric_id: str,
    metric_value: str = "",
    fact_id: str = "",
    skill_id: str = "",
    role_family_key: str = "",
    usage_count: int = 1,
    created_at: str | None = None,
) -> None:
    """Record metric usage memory for novelty-aware selection."""
    conn.execute(
        """
        INSERT INTO resume_metric_usage (
            run_id, resume_section, metric_id, metric_value, fact_id, skill_id,
            role_family_key, usage_count, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(run_id, resume_section, metric_id)
        DO UPDATE SET
            usage_count = resume_metric_usage.usage_count + excluded.usage_count,
            metric_value = excluded.metric_value,
            fact_id = excluded.fact_id,
            skill_id = excluded.skill_id,
            role_family_key = excluded.role_family_key
        """,
        (
            str(run_id),
            str(resume_section),
            str(metric_id),
            str(metric_value),
            str(fact_id),
            str(skill_id),
            str(role_family_key),
            max(1, int(usage_count or 1)),
            created_at or _utc_now(),
        ),
    )


def record_graph_selection_rejection(
    conn: sqlite3.Connection,
    *,
    run_id: str,
    section_id: str,
    candidate_node_id: str,
    candidate_node_type: str,
    rejected_reason: str,
    rejected_at_stage: str,
    competing_selected_node_id: str = "",
    path_signature: str = "",
    created_at: str | None = None,
) -> None:
    """Record why a graph candidate was rejected during selection."""
    conn.execute(
        """
        INSERT OR REPLACE INTO graph_selection_rejections (
            run_id, section_id, candidate_node_id, candidate_node_type,
            rejected_reason, rejected_at_stage, competing_selected_node_id,
            path_signature, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(run_id),
            str(section_id),
            str(candidate_node_id),
            str(candidate_node_type),
            str(rejected_reason),
            str(rejected_at_stage),
            str(competing_selected_node_id),
            str(path_signature),
            created_at or _utc_now(),
        ),
    )


def query_repeated_metrics(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return metrics used more than once, grouped by metric/value."""
    conn.row_factory = sqlite3.Row
    return [
        dict(row)
        for row in conn.execute(
            """
            SELECT metric_id, metric_value, SUM(usage_count) AS appearances,
                   GROUP_CONCAT(DISTINCT resume_section) AS sections
            FROM resume_metric_usage
            GROUP BY metric_id, metric_value
            HAVING SUM(usage_count) > 1
            ORDER BY appearances DESC, metric_id
            """
        ).fetchall()
    ]


def query_reverse_metric_paths(
    conn: sqlite3.Connection,
    *,
    metric_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return upstream edges/paths explaining why a metric or node is reachable."""
    conn.row_factory = sqlite3.Row
    return [
        dict(row)
        for row in conn.execute(
            """
            SELECT e.source_node_id AS upstream_node_id,
                   n.node_type AS upstream_node_type,
                   n.label AS upstream_label,
                   e.edge_type,
                   e.rationale,
                   e.projection_behavior,
                   e.external_claim_policy
            FROM graph_edges e
            LEFT JOIN graph_nodes n ON n.node_id = e.source_node_id
            WHERE e.target_node_id = ?
            ORDER BY e.edge_type, upstream_node_id
            LIMIT ?
            """,
            (str(metric_id), int(limit)),
        ).fetchall()
    ]


def query_sibling_alternatives(
    conn: sqlite3.Connection,
    *,
    node_id: str,
    limit: int = 10,
    include_diagnostics_only: bool = False,
) -> list[dict[str, Any]]:
    """Return nearby alternatives for a skill/fact/metric node."""
    conn.row_factory = sqlite3.Row
    extra = "" if include_diagnostics_only else "AND n.external_eligible = 1"
    return [
        dict(row)
        for row in conn.execute(
            f"""
            SELECT sib.sibling_node_id AS alternate_node_id,
                   n.node_type AS alternate_node_type,
                   n.label AS alternate_label,
                   sib.sibling_reason,
                   sib.shared_parent_node_id,
                   sib.shared_edge_type,
                   sib.sibling_score
            FROM graph_sibling_links sib
            JOIN graph_nodes n ON n.node_id = sib.sibling_node_id
            WHERE sib.node_id = ?
              {extra}
            ORDER BY sib.sibling_score DESC, sib.sibling_node_id
            LIMIT ?
            """,
            (str(node_id), int(limit)),
        ).fetchall()
    ]


def query_section_evidence_budget(
    conn: sqlite3.Connection,
    *,
    section_id: str,
    role_family_key: str,
) -> dict[str, Any] | None:
    """Return section evidence budget defaults for a role family."""
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT *
        FROM section_evidence_budget
        WHERE section_id = ? AND role_family_key = ?
        """,
        (str(section_id), str(role_family_key)),
    ).fetchone()
    return dict(row) if row is not None else None


def query_best_metric_candidates(
    conn: sqlite3.Connection,
    *,
    section_id: str,
    role_family_key: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return metric candidates ordered by low prior usage and graph strength."""
    conn.row_factory = sqlite3.Row
    return [
        dict(row)
        for row in conn.execute(
            """
            SELECT
                m.node_id AS metric_id,
                m.label AS metric_label,
                COALESCE(p.start_node_id, m.node_id) AS start_node_id,
                COALESCE(p.path_signature, m.node_id) AS path_signature,
                COALESCE(p.proof_strength_score, 0.0) AS proof_strength_score,
                COALESCE(p.novelty_score, 0.0) AS novelty_score,
                COALESCE(p.path_score, 0.0) AS path_score,
                COALESCE(SUM(u.usage_count), 0) AS prior_usage
            FROM graph_nodes m
            LEFT JOIN graph_paths p
              ON p.start_node_id = m.node_id OR p.end_node_id = m.node_id
            LEFT JOIN resume_metric_usage u
              ON u.metric_id = m.node_id
             AND (u.resume_section = ? OR u.role_family_key = ?)
            WHERE m.node_type = 'metric_outcome'
              AND (
                p.end_node_id = ?
                OR p.section_ids_json LIKE '%' || ? || '%'
                OR EXISTS (
                SELECT 1 FROM section_evidence_budget b
                WHERE b.section_id = ?
                  AND b.role_family_key = ?
                )
            )
            GROUP BY m.node_id, m.label, p.start_node_id, p.path_signature,
                     p.proof_strength_score, p.novelty_score, p.path_score
            ORDER BY prior_usage ASC,
                     p.proof_strength_score DESC,
                     p.path_score DESC,
                     p.novelty_score DESC,
                     m.node_id
            LIMIT ?
            """,
            (
                str(section_id),
                str(role_family_key),
                str(section_id),
                str(section_id),
                str(section_id),
                str(role_family_key),
                int(limit),
            ),
        ).fetchall()
    ]


__all__ = [
    "DEFAULT_MAX_DEPTH",
    "GRAPH_INDEX_OBJECTS",
    "GRAPH_INDEX_SCHEMA_VERSION",
    "build_graph_neighborhoods",
    "build_graph_index_rows",
    "build_graph_sibling_links",
    "build_reverse_edge_view",
    "materialize_graph_path_index",
    "query_best_metric_candidates",
    "query_repeated_metrics",
    "query_reverse_metric_paths",
    "query_section_evidence_budget",
    "query_sibling_alternatives",
    "record_graph_selection_rejection",
    "record_resume_metric_usage",
]
