"""SQLite graph-engine indexes for apps_rg augmented_skills_graph.

This module deliberately keeps SQLite as a generated projection of the
canonical JSON graph. It adds graphDB-like capabilities without introducing
a server dependency or changing graph authority:

* richer edge metadata preservation
* reverse traversal view
* materialized path index
* sibling-alternative index
* neighborhood index
* metric usage memory and novelty queries
* section evidence budgets
* selection rejection receipts

It is safe to run repeatedly. Generated tables are rebuilt with DELETE/INSERT;
source tables such as graph_nodes, graph_edges, and skill_fact_links are never
truncated by this module.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from agentic_core.L4_state.adapters import sqlite3_adapter as sqlite3

GRAPH_INDEX_SCHEMA_VERSION = "apps_rg.graph_sqlite_path_index.v1"

EDGE_METADATA_COLUMNS: tuple[tuple[str, str], ...] = (
    ("rationale", "TEXT NOT NULL DEFAULT ''"),
    ("projection_behavior", "TEXT NOT NULL DEFAULT ''"),
    ("external_claim_policy", "TEXT NOT NULL DEFAULT ''"),
    ("validation_status", "TEXT NOT NULL DEFAULT ''"),
    ("edge_note", "TEXT NOT NULL DEFAULT ''"),
    ("operator_note", "TEXT NOT NULL DEFAULT ''"),
    ("business_story", "TEXT NOT NULL DEFAULT ''"),
    ("technical_story", "TEXT NOT NULL DEFAULT ''"),
)

DEFAULT_SECTION_BUDGETS: tuple[dict[str, Any], ...] = (
    {
        "section_id": "executive_summary",
        "role_family_key": "*",
        "max_metric_reuse": 1,
        "max_fact_family_reuse": 2,
        "required_node_types": ["skill", "fact", "metric_outcome"],
        "preferred_edge_types": ["role_family_weights_pillar", "skill_supported_by_fact", "fact_has_metric_outcome"],
        "forbidden_metric_ids": [],
        "preferred_metric_families": ["revenue_growth", "risk_governance", "platform_scale", "adoption_enablement"],
    },
    {
        "section_id": "competencies",
        "role_family_key": "*",
        "max_metric_reuse": 0,
        "max_fact_family_reuse": 1,
        "required_node_types": ["skill", "pillar"],
        "preferred_edge_types": ["capability_domain_contains_skill", "pillar_contains_skill"],
        "forbidden_metric_ids": [],
        "preferred_metric_families": ["platform_scale", "model_quality", "delivery_velocity"],
    },
    {
        "section_id": "experience",
        "role_family_key": "*",
        "max_metric_reuse": 1,
        "max_fact_family_reuse": 2,
        "required_node_types": ["skill", "fact", "metric_outcome"],
        "preferred_edge_types": ["skill_supported_by_fact", "employment_hosts_fact", "fact_has_metric_outcome"],
        "forbidden_metric_ids": [],
        "preferred_metric_families": ["cost_efficiency", "revenue_growth", "delivery_velocity"],
    },
    {
        "section_id": "leadership",
        "role_family_key": "*",
        "max_metric_reuse": 1,
        "max_fact_family_reuse": 2,
        "required_node_types": ["skill", "fact"],
        "preferred_edge_types": ["role_family_weights_pillar", "employment_hosts_fact", "skill_supported_by_fact"],
        "forbidden_metric_ids": [],
        "preferred_metric_families": ["revenue_growth", "adoption_enablement", "partner_gtm"],
    },
    {
        "section_id": "technical_architecture",
        "role_family_key": "*",
        "max_metric_reuse": 1,
        "max_fact_family_reuse": 2,
        "required_node_types": ["skill", "fact", "metric_outcome"],
        "preferred_edge_types": ["capability_domain_contains_skill", "skill_supported_by_fact", "fact_has_metric_outcome"],
        "forbidden_metric_ids": [],
        "preferred_metric_families": ["platform_scale", "risk_governance", "model_quality"],
    },
)

GRAPHDB_CAPABILITY_DDL: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS graph_paths (
        path_id TEXT PRIMARY KEY,
        start_node_id TEXT NOT NULL,
        end_node_id TEXT NOT NULL,
        path_depth INTEGER NOT NULL,
        path_signature TEXT NOT NULL,
        node_path_json TEXT NOT NULL,
        edge_path_json TEXT NOT NULL,
        edge_types_json TEXT NOT NULL,
        proof_fact_ids_json TEXT NOT NULL DEFAULT '[]',
        metric_ids_json TEXT NOT NULL DEFAULT '[]',
        section_ids_json TEXT NOT NULL DEFAULT '[]',
        path_score REAL NOT NULL DEFAULT 0.0,
        novelty_score REAL NOT NULL DEFAULT 0.0,
        proof_strength_score REAL NOT NULL DEFAULT 0.0,
        created_at TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_graph_paths_start ON graph_paths(start_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_graph_paths_end ON graph_paths(end_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_graph_paths_depth ON graph_paths(path_depth)",
    """
    CREATE TABLE IF NOT EXISTS graph_sibling_links (
        node_id TEXT NOT NULL,
        sibling_node_id TEXT NOT NULL,
        sibling_reason TEXT NOT NULL DEFAULT '',
        shared_parent_node_id TEXT NOT NULL DEFAULT '',
        shared_edge_type TEXT NOT NULL DEFAULT '',
        sibling_score REAL NOT NULL DEFAULT 0.0,
        PRIMARY KEY (node_id, sibling_node_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_sibling_node ON graph_sibling_links(node_id)",
    "CREATE INDEX IF NOT EXISTS idx_sibling_peer ON graph_sibling_links(sibling_node_id)",
    """
    CREATE TABLE IF NOT EXISTS graph_neighborhoods (
        center_node_id TEXT NOT NULL,
        neighbor_node_id TEXT NOT NULL,
        distance INTEGER NOT NULL,
        connecting_path_json TEXT NOT NULL,
        edge_types_json TEXT NOT NULL,
        relationship_summary TEXT NOT NULL DEFAULT '',
        neighbor_score REAL NOT NULL DEFAULT 0.0,
        PRIMARY KEY (center_node_id, neighbor_node_id, distance)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_neighborhood_center ON graph_neighborhoods(center_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_neighborhood_neighbor ON graph_neighborhoods(neighbor_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_neighborhood_distance ON graph_neighborhoods(distance)",
    """
    CREATE TABLE IF NOT EXISTS resume_metric_usage (
        run_id TEXT NOT NULL,
        resume_section TEXT NOT NULL,
        metric_id TEXT NOT NULL,
        metric_value TEXT NOT NULL DEFAULT '',
        fact_id TEXT NOT NULL DEFAULT '',
        skill_id TEXT NOT NULL DEFAULT '',
        role_family_key TEXT NOT NULL DEFAULT '',
        usage_count INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        PRIMARY KEY (run_id, resume_section, metric_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_metric ON resume_metric_usage(metric_id)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_section ON resume_metric_usage(resume_section)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_fact ON resume_metric_usage(fact_id)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_skill ON resume_metric_usage(skill_id)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_role ON resume_metric_usage(role_family_key)",
    """
    CREATE TABLE IF NOT EXISTS section_evidence_budget (
        section_id TEXT NOT NULL,
        role_family_key TEXT NOT NULL,
        max_metric_reuse INTEGER NOT NULL DEFAULT 1,
        max_fact_family_reuse INTEGER NOT NULL DEFAULT 2,
        required_node_types_json TEXT NOT NULL DEFAULT '[]',
        preferred_edge_types_json TEXT NOT NULL DEFAULT '[]',
        forbidden_metric_ids_json TEXT NOT NULL DEFAULT '[]',
        preferred_metric_families_json TEXT NOT NULL DEFAULT '[]',
        PRIMARY KEY (section_id, role_family_key)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS graph_selection_rejections (
        run_id TEXT NOT NULL,
        section_id TEXT NOT NULL,
        candidate_node_id TEXT NOT NULL,
        candidate_node_type TEXT NOT NULL,
        rejected_reason TEXT NOT NULL,
        rejected_at_stage TEXT NOT NULL,
        competing_selected_node_id TEXT NOT NULL DEFAULT '',
        path_signature TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        PRIMARY KEY (run_id, section_id, candidate_node_id, rejected_at_stage)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_rejections_run_section ON graph_selection_rejections(run_id, section_id)",
    "CREATE INDEX IF NOT EXISTS idx_rejections_candidate ON graph_selection_rejections(candidate_node_id)",
)

HIGH_VALUE_NODE_TYPES = frozenset(
    {"role_family", "career_track", "pillar", "skill", "fact", "metric_outcome", "section"}
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    try:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    except Exception as exc:
        # Import the governed adapter only on the exceptional path. A module-
        # level import causes agentic_core reachability to load this apps module
        # again before its public functions exist.
        from agentic_core.L4_state.adapters import sqlite3_adapter

        if not isinstance(exc, sqlite3_adapter.DatabaseError):
            raise
        return set()
    return {str(r[1]) for r in rows}


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    return bool(row)


def _node_type_map(conn: sqlite3.Connection) -> dict[str, str]:
    if not table_exists(conn, "graph_nodes"):
        return {}
    return {
        str(node_id): str(node_type)
        for node_id, node_type in conn.execute("SELECT node_id, node_type FROM graph_nodes")
    }


def _eligible_node_ids(conn: sqlite3.Connection) -> set[str]:
    if not table_exists(conn, "graph_nodes"):
        return set()
    cols = table_columns(conn, "graph_nodes")
    if {"node_id", "activation_status", "support_level"}.issubset(cols):
        blocked_statuses = ("DRAFT", "INTERNAL_ONLY", "DO_NOT_PROMOTE", "BLOCKED")
        blocked_support = ("INTERNAL_ONLY", "REPO_EVIDENCE_PORTFOLIO", "TARGETING_ONLY", "STYLE_ONLY", "BLOCKED")
        return {
            str(r[0])
            for r in conn.execute(
                """
                SELECT node_id FROM graph_nodes
                WHERE COALESCE(activation_status,'') NOT IN (?,?,?,?)
                  AND COALESCE(support_level,'') NOT IN (?,?,?,?,?)
                """,
                (*blocked_statuses, *blocked_support),
            ).fetchall()
        }
    return {str(r[0]) for r in conn.execute("SELECT node_id FROM graph_nodes")}


def ensure_graphdb_capability_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    """Install additive SQLite graphDB-like schema; never drops source rows."""
    added_columns: list[str] = []
    if table_exists(conn, "graph_edges"):
        cols = table_columns(conn, "graph_edges")
        for col, ddl_type in EDGE_METADATA_COLUMNS:
            if col not in cols:
                conn.execute(f"ALTER TABLE graph_edges ADD COLUMN {col} {ddl_type}")
                added_columns.append(col)
    for ddl in GRAPHDB_CAPABILITY_DDL:
        conn.execute(ddl)
    build_reverse_edge_view(conn)
    seed_section_evidence_budgets(conn)
    conn.commit()
    return {
        "schema_status": "GRAPHDB_CAPABILITY_SCHEMA_READY",
        "added_graph_edges_columns": added_columns,
        "tables": sorted(
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN (?,?,?,?,?,?)",
                (
                    "graph_paths",
                    "graph_sibling_links",
                    "graph_neighborhoods",
                    "resume_metric_usage",
                    "section_evidence_budget",
                    "graph_selection_rejections",
                ),
            )
        ),
        "reverse_view_exists": table_exists(conn, "graph_edges_reverse"),
    }


def build_reverse_edge_view(conn: sqlite3.Connection) -> None:
    """Create a target-to-source edge view for reverse traversal."""
    if not table_exists(conn, "graph_edges"):
        return
    conn.execute("DROP VIEW IF EXISTS graph_edges_reverse")
    cols = table_columns(conn, "graph_edges")

    def col(name: str, fallback: str = "''") -> str:
        return name if name in cols else f"{fallback} AS {name}"

    conn.execute(
        f"""
        CREATE VIEW graph_edges_reverse AS
        SELECT
            edge_id,
            target_node_id AS source_node_id,
            source_node_id AS target_node_id,
            edge_type || '_reverse' AS edge_type,
            {col('edge_family')},
            {col('weight', '1.0')},
            {col('confidence')},
            {col('evidence_status')},
            {col('section_fit')},
            {col('source_authority', "'augmented_skills_graph'")},
            {col('rationale')},
            {col('projection_behavior')},
            {col('external_claim_policy')},
            {col('validation_status')}
        FROM graph_edges
        """
    )
    conn.commit()


def seed_section_evidence_budgets(conn: sqlite3.Connection) -> None:
    for row in DEFAULT_SECTION_BUDGETS:
        conn.execute(
            """
            INSERT OR IGNORE INTO section_evidence_budget (
                section_id, role_family_key, max_metric_reuse, max_fact_family_reuse,
                required_node_types_json, preferred_edge_types_json,
                forbidden_metric_ids_json, preferred_metric_families_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["section_id"],
                row["role_family_key"],
                int(row["max_metric_reuse"]),
                int(row["max_fact_family_reuse"]),
                _json(row["required_node_types"]),
                _json(row["preferred_edge_types"]),
                _json(row["forbidden_metric_ids"]),
                _json(row["preferred_metric_families"]),
            ),
        )
    conn.commit()


def _edge_tuples(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    if not table_exists(conn, "graph_edges"):
        return []
    cols = table_columns(conn, "graph_edges")
    base = ["edge_id", "source_node_id", "target_node_id", "edge_type"]
    optional = ["weight", "confidence", "section_fit", "rationale", "validation_status"]
    select_cols = base + [c for c in optional if c in cols]
    rows = conn.execute(f"SELECT {','.join(select_cols)} FROM graph_edges").fetchall()
    out: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(zip(select_cols, raw, strict=False))
        out.append(row)
    return out


def build_graph_index_rows(
    *,
    node_rows: Iterable[dict[str, Any]],
    edge_rows: Iterable[dict[str, Any]],
    section_rows: Iterable[dict[str, Any]],
    role_family_projection_rows: Iterable[dict[str, Any]],
    created_at: str,
) -> dict[str, list[dict[str, Any]]]:
    """Build generated graph-index rows before the SQLite file exists."""
    nodes = {str(row.get("node_id") or ""): dict(row) for row in node_rows if row.get("node_id")}
    edges = [dict(row) for row in edge_rows]
    node_types = {node_id: str(row.get("node_type") or "") for node_id, row in nodes.items()}

    graph_paths: list[dict[str, Any]] = []
    for edge in edges:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        if not src or not tgt:
            continue
        edge_id = str(edge.get("edge_id") or _digest(f"{src}->{tgt}")[:16])
        edge_type = str(edge.get("edge_type") or "")
        facts = [node_id for node_id in (src, tgt) if node_types.get(node_id) == "fact" or node_id.startswith("fact_")]
        metrics = [
            node_id
            for node_id in (src, tgt)
            if node_types.get(node_id) == "metric_outcome" or node_id.startswith("metric_")
        ]
        sections = [
            node_id
            for node_id in (src, tgt)
            if node_types.get(node_id) == "section" or node_id.startswith("section_")
        ]
        proof_score = min(1.0, 0.25 * len(facts) + 0.20 * len(metrics) + 0.15 * len(sections))
        novelty_score = 1.0 / max(1, len(metrics) + len(facts))
        path_score = round(proof_score + novelty_score + 0.5, 6)
        signature = f"{src}->{tgt}"
        path_identity = f"{signature}|{edge_id}"
        graph_paths.append(
            {
                "path_id": f"path:{_digest(path_identity)[:24]}",
                "start_node_id": src,
                "end_node_id": tgt,
                "path_depth": 1,
                "path_signature": signature,
                "node_path_json": _json([src, tgt]),
                "edge_path_json": _json([edge_id]),
                "edge_types_json": _json([edge_type]),
                "proof_fact_ids_json": _json(facts),
                "metric_ids_json": _json(metrics),
                "section_ids_json": _json(sections),
                "path_score": path_score,
                "novelty_score": round(novelty_score, 6),
                "proof_strength_score": round(proof_score, 6),
                "created_at": created_at,
            }
        )

    children_by_parent: dict[tuple[str, str], list[str]] = defaultdict(list)
    for edge in edges:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        edge_type = str(edge.get("edge_type") or "")
        if src and tgt and tgt in nodes and node_types.get(tgt) == "skill":
            children_by_parent[(src, edge_type)].append(tgt)

    graph_sibling_links: list[dict[str, Any]] = []
    sibling_keys: set[tuple[str, str]] = set()
    for (parent, edge_type), children in sorted(children_by_parent.items()):
        unique = sorted(set(children))
        if len(unique) < 2:
            continue
        for node_id in unique:
            for sibling_node_id in unique:
                if node_id == sibling_node_id:
                    continue
                key = (node_id, sibling_node_id)
                if key in sibling_keys:
                    continue
                sibling_keys.add(key)
                score = 1.0 + (0.5 if node_types.get(node_id) == node_types.get(sibling_node_id) else 0.0)
                graph_sibling_links.append(
                    {
                        "node_id": node_id,
                        "sibling_node_id": sibling_node_id,
                        "sibling_reason": f"shared_parent:{edge_type}",
                        "shared_parent_node_id": parent,
                        "shared_edge_type": edge_type,
                        "sibling_score": round(score, 4),
                    }
                )

    adjacency: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for edge in edges:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        edge_type = str(edge.get("edge_type") or "")
        if src and tgt:
            adjacency[src].append((tgt, edge_type))
            adjacency[tgt].append((src, f"{edge_type}_reverse"))

    graph_neighborhoods: list[dict[str, Any]] = []
    neighborhood_keys: set[tuple[str, str, int]] = set()
    for center, neighbors in sorted(adjacency.items()):
        for neighbor, edge_type in sorted(set(neighbors)):
            key = (center, neighbor, 1)
            if key in neighborhood_keys:
                continue
            neighborhood_keys.add(key)
            graph_neighborhoods.append(
                {
                    "center_node_id": center,
                    "neighbor_node_id": neighbor,
                    "distance": 1,
                    "connecting_path_json": _json([center, neighbor]),
                    "edge_types_json": _json([edge_type]),
                    "relationship_summary": f"1_hop:{edge_type}",
                    "neighbor_score": round(1.0 + (0.5 if node_types.get(neighbor) in HIGH_VALUE_NODE_TYPES else 0.0), 6),
                }
            )

    role_family_keys = {"*"}
    for row in role_family_projection_rows:
        key = str(row.get("role_family_id") or row.get("projection_role_family_key") or "")
        if key:
            role_family_keys.add(key)
    for row in section_rows:
        key = str(row.get("role_family_key") or "")
        if key:
            role_family_keys.add(key)

    section_evidence_budget: list[dict[str, Any]] = []
    for role_family_key in sorted(role_family_keys):
        for budget in DEFAULT_SECTION_BUDGETS:
            section_evidence_budget.append(
                {
                    "section_id": budget["section_id"],
                    "role_family_key": role_family_key,
                    "max_metric_reuse": int(budget["max_metric_reuse"]),
                    "max_fact_family_reuse": int(budget["max_fact_family_reuse"]),
                    "required_node_types_json": _json(budget["required_node_types"]),
                    "preferred_edge_types_json": _json(budget["preferred_edge_types"]),
                    "forbidden_metric_ids_json": _json(budget["forbidden_metric_ids"]),
                    "preferred_metric_families_json": _json(budget["preferred_metric_families"]),
                }
            )

    return {
        "graph_paths": graph_paths,
        "graph_neighborhoods": graph_neighborhoods,
        "graph_sibling_links": graph_sibling_links,
        "section_evidence_budget": section_evidence_budget,
    }


def materialize_graph_path_index(
    conn: sqlite3.Connection,
    *,
    max_depth: int = 4,
    max_paths: int = 20000,
) -> dict[str, Any]:
    """Precompute high-value directed paths up to max_depth."""
    ensure_graphdb_capability_schema(conn)
    node_types = _node_type_map(conn)
    edges = _edge_tuples(conn)
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        if src and tgt:
            adjacency[src].append(edge)

    seed_nodes = [n for n, t in node_types.items() if t in HIGH_VALUE_NODE_TYPES]
    if not seed_nodes:
        seed_nodes = sorted(adjacency)[:1000]

    conn.execute("DELETE FROM graph_paths")
    created = 0
    now = _utc_now()
    for start in sorted(seed_nodes):
        queue: deque[tuple[str, list[str], list[dict[str, Any]]]] = deque()
        queue.append((start, [start], []))
        while queue and created < max_paths:
            current, node_path, edge_path = queue.popleft()
            if len(edge_path) >= max_depth:
                continue
            for edge in adjacency.get(current, []):
                nxt = str(edge.get("target_node_id") or "")
                if not nxt or nxt in node_path:
                    continue
                new_nodes = node_path + [nxt]
                new_edges = edge_path + [edge]
                depth = len(new_edges)
                end_type = node_types.get(nxt, "")
                edge_types = [str(e.get("edge_type") or "") for e in new_edges]
                facts = [n for n in new_nodes if node_types.get(n) == "fact" or n.startswith("fact_") or n.startswith("node_fact:")]
                metrics = [n for n in new_nodes if node_types.get(n) == "metric_outcome" or n.startswith("metric_")]
                sections = [n for n in new_nodes if node_types.get(n) == "section" or n.startswith("section_")]
                high_value = bool(facts or metrics or sections or end_type in {"skill", "fact", "metric_outcome", "section"})
                if high_value and depth >= 1:
                    sig = "->".join(new_nodes)
                    path_id = f"path:{_digest(sig)[:24]}"
                    proof_score = min(1.0, 0.25 * len(facts) + 0.20 * len(metrics) + 0.15 * len(sections))
                    novelty_score = 1.0 / max(1, len(metrics) + len(facts))
                    path_score = round(proof_score + novelty_score + (1.0 / (1 + depth)), 6)
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO graph_paths (
                            path_id, start_node_id, end_node_id, path_depth, path_signature,
                            node_path_json, edge_path_json, edge_types_json, proof_fact_ids_json,
                            metric_ids_json, section_ids_json, path_score, novelty_score,
                            proof_strength_score, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            path_id,
                            start,
                            nxt,
                            depth,
                            sig,
                            _json(new_nodes),
                            _json([e.get("edge_id", "") for e in new_edges]),
                            _json(edge_types),
                            _json(facts),
                            _json(metrics),
                            _json(sections),
                            path_score,
                            round(novelty_score, 6),
                            round(proof_score, 6),
                            now,
                        ),
                    )
                    created += 1
                queue.append((nxt, new_nodes, new_edges))
                if created >= max_paths:
                    break
    conn.commit()
    return {"graph_paths_materialized": created, "max_depth": max_depth}


def build_graph_sibling_links(conn: sqlite3.Connection) -> dict[str, Any]:
    """Build skill/metric/fact sibling links from shared parents."""
    ensure_graphdb_capability_schema(conn)
    node_types = _node_type_map(conn)
    eligible = _eligible_node_ids(conn)
    edges = _edge_tuples(conn)
    children_by_parent: dict[tuple[str, str], list[str]] = defaultdict(list)
    for edge in edges:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        et = str(edge.get("edge_type") or "")
        if not src or not tgt:
            continue
        if node_types.get(tgt) in {"skill", "fact", "metric_outcome"} or tgt.startswith(("skill_", "fact_", "metric_")):
            if eligible and tgt not in eligible and node_types.get(tgt) == "skill":
                continue
            children_by_parent[(src, et)].append(tgt)

    conn.execute("DELETE FROM graph_sibling_links")
    inserted = 0
    for (parent, et), children in children_by_parent.items():
        unique = sorted(set(children))
        if len(unique) < 2:
            continue
        for node_id in unique:
            for sibling in unique:
                if node_id == sibling:
                    continue
                score = 1.0
                if node_types.get(node_id) == node_types.get(sibling):
                    score += 0.5
                conn.execute(
                    """
                    INSERT OR REPLACE INTO graph_sibling_links (
                        node_id, sibling_node_id, sibling_reason, shared_parent_node_id,
                        shared_edge_type, sibling_score
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        node_id,
                        sibling,
                        f"shared_parent:{parent};edge_type:{et}",
                        parent,
                        et,
                        round(score, 4),
                    ),
                )
                inserted += 1
    conn.commit()
    return {"graph_sibling_links_materialized": inserted}


def build_graph_neighborhoods(
    conn: sqlite3.Connection,
    *,
    max_distance: int = 3,
    max_centers: int = 1500,
) -> dict[str, Any]:
    """Build undirected N-hop neighborhoods for high-value nodes."""
    ensure_graphdb_capability_schema(conn)
    node_types = _node_type_map(conn)
    edges = _edge_tuples(conn)
    adjacency: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for e in edges:
        src, tgt, et, eid = str(e.get("source_node_id") or ""), str(e.get("target_node_id") or ""), str(e.get("edge_type") or ""), str(e.get("edge_id") or "")
        if src and tgt:
            adjacency[src].append((tgt, et, eid))
            adjacency[tgt].append((src, et + "_reverse", eid))
    centers = [n for n, t in node_types.items() if t in HIGH_VALUE_NODE_TYPES][:max_centers]
    if not centers:
        centers = sorted(adjacency)[:max_centers]
    conn.execute("DELETE FROM graph_neighborhoods")
    inserted = 0
    for center in centers:
        seen = {center}
        queue: deque[tuple[str, int, list[str], list[str]]] = deque([(center, 0, [center], [])])
        while queue:
            current, dist, path, edge_types = queue.popleft()
            if dist >= max_distance:
                continue
            for neighbor, et, _eid in adjacency.get(current, []):
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                npath = path + [neighbor]
                netypes = edge_types + [et]
                ndist = dist + 1
                ntype = node_types.get(neighbor, "")
                score = round((1.0 / ndist) + (0.5 if ntype in HIGH_VALUE_NODE_TYPES else 0.0), 6)
                conn.execute(
                    """
                    INSERT OR REPLACE INTO graph_neighborhoods (
                        center_node_id, neighbor_node_id, distance, connecting_path_json,
                        edge_types_json, relationship_summary, neighbor_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        center,
                        neighbor,
                        ndist,
                        _json(npath),
                        _json(netypes),
                        f"{ndist}_hop:{'|'.join(netypes)}",
                        score,
                    ),
                )
                inserted += 1
                queue.append((neighbor, ndist, npath, netypes))
    conn.commit()
    return {"graph_neighborhoods_materialized": inserted, "max_distance": max_distance}


def materialize_graphdb_capability_indexes(conn: sqlite3.Connection) -> dict[str, Any]:
    """Run all additive graphDB-like SQLite index builders."""
    out = {"schema": ensure_graphdb_capability_schema(conn)}
    out["paths"] = materialize_graph_path_index(conn)
    out["siblings"] = build_graph_sibling_links(conn)
    out["neighborhoods"] = build_graph_neighborhoods(conn)
    return out


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
) -> None:
    ensure_graphdb_capability_schema(conn)
    conn.execute(
        """
        INSERT INTO resume_metric_usage (
            run_id, resume_section, metric_id, metric_value, fact_id, skill_id,
            role_family_key, usage_count, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(run_id, resume_section, metric_id)
        DO UPDATE SET usage_count = usage_count + excluded.usage_count
        """,
        (run_id, resume_section, metric_id, metric_value, fact_id, skill_id, role_family_key, int(usage_count), _utc_now()),
    )
    conn.commit()


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
) -> None:
    ensure_graphdb_capability_schema(conn)
    conn.execute(
        """
        INSERT OR REPLACE INTO graph_selection_rejections (
            run_id, section_id, candidate_node_id, candidate_node_type, rejected_reason,
            rejected_at_stage, competing_selected_node_id, path_signature, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            section_id,
            candidate_node_id,
            candidate_node_type,
            rejected_reason,
            rejected_at_stage,
            competing_selected_node_id,
            path_signature,
            _utc_now(),
        ),
    )
    conn.commit()


def query_repeated_metrics(conn: sqlite3.Connection, *, min_count: int = 2) -> list[dict[str, Any]]:
    ensure_graphdb_capability_schema(conn)
    return [
        {
            "metric_id": r[0],
            "metric_value": r[1],
            "appearances": r[2],
            "sections": (r[3] or "").split(",") if r[3] else [],
        }
        for r in conn.execute(
            """
            SELECT metric_id, metric_value, SUM(usage_count) AS appearances,
                   GROUP_CONCAT(DISTINCT resume_section) AS sections
            FROM resume_metric_usage
            GROUP BY metric_id, metric_value
            HAVING SUM(usage_count) >= ?
            ORDER BY appearances DESC, metric_id
            """,
            (min_count,),
        )
    ]


def query_reverse_metric_paths(
    conn: sqlite3.Connection,
    *,
    metric_id: str,
    max_depth: int = 4,
    limit: int = 100,
) -> list[dict[str, Any]]:
    ensure_graphdb_capability_schema(conn)
    return [
        {
            "path_id": r[0],
            "start_node_id": r[1],
            "end_node_id": r[2],
            "path_depth": r[3],
            "path_signature": r[4],
            "node_path": json.loads(r[5]),
            "edge_types": json.loads(r[6]),
            "path_score": r[7],
        }
        for r in conn.execute(
            """
            SELECT path_id, start_node_id, end_node_id, path_depth, path_signature,
                   node_path_json, edge_types_json, path_score
            FROM graph_paths
            WHERE end_node_id = ? AND path_depth <= ?
            ORDER BY path_score DESC, path_depth ASC
            LIMIT ?
            """,
            (metric_id, max_depth, limit),
        )
    ]


def query_sibling_alternatives(conn: sqlite3.Connection, *, node_id: str, limit: int = 25) -> list[dict[str, Any]]:
    ensure_graphdb_capability_schema(conn)
    return [
        {
            "node_id": node_id,
            "sibling_node_id": r[0],
            "sibling_label": r[1],
            "sibling_reason": r[2],
            "shared_parent_node_id": r[3],
            "shared_edge_type": r[4],
            "sibling_score": r[5],
        }
        for r in conn.execute(
            """
            SELECT s.sibling_node_id, COALESCE(n.label, ''), s.sibling_reason,
                   s.shared_parent_node_id, s.shared_edge_type, s.sibling_score
            FROM graph_sibling_links s
            LEFT JOIN graph_nodes n ON n.node_id = s.sibling_node_id
            WHERE s.node_id = ?
            ORDER BY s.sibling_score DESC, s.sibling_node_id
            LIMIT ?
            """,
            (node_id, limit),
        )
    ]


def query_section_evidence_budget(
    conn: sqlite3.Connection,
    *,
    section_id: str,
    role_family_key: str = "*",
) -> dict[str, Any] | None:
    ensure_graphdb_capability_schema(conn)
    row = conn.execute(
        """
        SELECT section_id, role_family_key, max_metric_reuse, max_fact_family_reuse,
               required_node_types_json, preferred_edge_types_json,
               forbidden_metric_ids_json, preferred_metric_families_json
        FROM section_evidence_budget
        WHERE section_id = ? AND role_family_key IN (?, '*')
        ORDER BY CASE WHEN role_family_key = ? THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (section_id, role_family_key, role_family_key),
    ).fetchone()
    if not row:
        return None
    return {
        "section_id": row[0],
        "role_family_key": row[1],
        "max_metric_reuse": row[2],
        "max_fact_family_reuse": row[3],
        "required_node_types": json.loads(row[4]),
        "preferred_edge_types": json.loads(row[5]),
        "forbidden_metric_ids": json.loads(row[6]),
        "preferred_metric_families": json.loads(row[7]),
    }


def query_best_metric_candidates(
    conn: sqlite3.Connection,
    *,
    role_family_key: str = "",
    section_id: str = "executive_summary",
    limit: int = 25,
) -> list[dict[str, Any]]:
    """Return metric candidates prioritized by novelty and path/proof score."""
    ensure_graphdb_capability_schema(conn)
    budget = query_section_evidence_budget(conn, section_id=section_id, role_family_key=role_family_key) or {}
    forbidden = set(budget.get("forbidden_metric_ids") or [])
    rows = conn.execute(
        """
        SELECT p.end_node_id, COALESCE(n.label, p.end_node_id), p.start_node_id,
               p.path_signature, p.path_score, p.novelty_score, p.proof_strength_score,
               COALESCE(SUM(u.usage_count), 0) AS prior_usage
        FROM graph_paths p
        LEFT JOIN graph_nodes n ON n.node_id = p.end_node_id
        LEFT JOIN resume_metric_usage u ON u.metric_id = p.end_node_id
        WHERE (n.node_type = 'metric_outcome' OR p.end_node_id LIKE 'metric_%')
        GROUP BY p.end_node_id, n.label, p.start_node_id, p.path_signature,
                 p.path_score, p.novelty_score, p.proof_strength_score
        ORDER BY prior_usage ASC, p.proof_strength_score DESC, p.novelty_score DESC, p.path_score DESC
        LIMIT ?
        """,
        (max(limit * 2, limit),),
    ).fetchall()
    out = []
    for r in rows:
        if r[0] in forbidden:
            continue
        out.append(
            {
                "metric_id": r[0],
                "metric_label": r[1],
                "start_node_id": r[2],
                "path_signature": r[3],
                "path_score": r[4],
                "novelty_score": r[5],
                "proof_strength_score": r[6],
                "prior_usage": r[7],
            }
        )
        if len(out) >= limit:
            break
    return out


__all__ = [
    "GRAPH_INDEX_SCHEMA_VERSION",
    "EDGE_METADATA_COLUMNS",
    "build_graph_index_rows",
    "ensure_graphdb_capability_schema",
    "build_reverse_edge_view",
    "materialize_graph_path_index",
    "build_graph_sibling_links",
    "build_graph_neighborhoods",
    "materialize_graphdb_capability_indexes",
    "record_resume_metric_usage",
    "record_graph_selection_rejection",
    "query_repeated_metrics",
    "query_reverse_metric_paths",
    "query_sibling_alternatives",
    "query_section_evidence_budget",
    "query_best_metric_candidates",
    "table_columns",
    "table_exists",
]
