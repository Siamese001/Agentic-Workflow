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

GRAPH_INDEX_CAPABILITY_VERSION = "apps_rg.graph_index_capability.v1.direct_only"
GRAPH_INDEX_SCHEMA_VERSION = "apps_rg.graph_sqlite_path_index.v6.direct_only_lossless_typed_digest"

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
        "preferred_edge_types": [
            "role_family_weights_pillar",
            "skill_supported_by_fact",
            "fact_has_metric_outcome",
        ],
        "forbidden_metric_ids": [],
        "preferred_metric_families": [
            "revenue_growth",
            "risk_governance",
            "platform_scale",
            "adoption_enablement",
        ],
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
        "preferred_edge_types": [
            "skill_supported_by_fact",
            "employment_hosts_fact",
            "fact_has_metric_outcome",
        ],
        "forbidden_metric_ids": [],
        "preferred_metric_families": ["cost_efficiency", "revenue_growth", "delivery_velocity"],
    },
    {
        "section_id": "leadership",
        "role_family_key": "*",
        "max_metric_reuse": 1,
        "max_fact_family_reuse": 2,
        "required_node_types": ["skill", "fact"],
        "preferred_edge_types": [
            "role_family_weights_pillar",
            "employment_hosts_fact",
            "skill_supported_by_fact",
        ],
        "forbidden_metric_ids": [],
        "preferred_metric_families": ["revenue_growth", "adoption_enablement", "partner_gtm"],
    },
    {
        "section_id": "technical_architecture",
        "role_family_key": "*",
        "max_metric_reuse": 1,
        "max_fact_family_reuse": 2,
        "required_node_types": ["skill", "fact", "metric_outcome"],
        "preferred_edge_types": [
            "capability_domain_contains_skill",
            "skill_supported_by_fact",
            "fact_has_metric_outcome",
        ],
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
        path_depth INTEGER NOT NULL CHECK (path_depth >= 1),
        path_signature TEXT NOT NULL,
        node_path_json TEXT NOT NULL
            CHECK (json_valid(node_path_json) AND json_type(node_path_json) = 'array'),
        edge_path_json TEXT NOT NULL
            CHECK (json_valid(edge_path_json) AND json_type(edge_path_json) = 'array'),
        edge_types_json TEXT NOT NULL
            CHECK (json_valid(edge_types_json) AND json_type(edge_types_json) = 'array'),
        proof_fact_ids_json TEXT NOT NULL DEFAULT '[]'
            CHECK (json_valid(proof_fact_ids_json) AND json_type(proof_fact_ids_json) = 'array'),
        metric_ids_json TEXT NOT NULL DEFAULT '[]'
            CHECK (json_valid(metric_ids_json) AND json_type(metric_ids_json) = 'array'),
        section_ids_json TEXT NOT NULL DEFAULT '[]'
            CHECK (json_valid(section_ids_json) AND json_type(section_ids_json) = 'array'),
        path_score REAL NOT NULL DEFAULT 0.0,
        novelty_score REAL NOT NULL DEFAULT 0.0,
        proof_strength_score REAL NOT NULL DEFAULT 0.0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (start_node_id) REFERENCES graph_nodes(node_id),
        FOREIGN KEY (end_node_id) REFERENCES graph_nodes(node_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_graph_paths_start ON graph_paths(start_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_graph_paths_end ON graph_paths(end_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_graph_paths_depth ON graph_paths(path_depth)",
    "CREATE INDEX IF NOT EXISTS idx_graph_paths_end_depth_score ON graph_paths(end_node_id, path_depth, path_score DESC)",
    """
    CREATE TABLE IF NOT EXISTS graph_sibling_links (
        node_id TEXT NOT NULL,
        sibling_node_id TEXT NOT NULL,
        sibling_reason TEXT NOT NULL DEFAULT '',
        shared_parent_node_id TEXT NOT NULL DEFAULT '',
        shared_edge_type TEXT NOT NULL DEFAULT '',
        sibling_score REAL NOT NULL DEFAULT 0.0,
        PRIMARY KEY (
            node_id, sibling_node_id, shared_parent_node_id, shared_edge_type
        ),
        CHECK (node_id <> sibling_node_id),
        FOREIGN KEY (node_id) REFERENCES graph_nodes(node_id),
        FOREIGN KEY (sibling_node_id) REFERENCES graph_nodes(node_id),
        FOREIGN KEY (shared_parent_node_id) REFERENCES graph_nodes(node_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_sibling_node ON graph_sibling_links(node_id)",
    "CREATE INDEX IF NOT EXISTS idx_sibling_peer ON graph_sibling_links(sibling_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_sibling_node_score ON graph_sibling_links(node_id, sibling_score DESC)",
    "CREATE INDEX IF NOT EXISTS idx_sibling_context_lookup ON graph_sibling_links(node_id, sibling_node_id, shared_parent_node_id, shared_edge_type)",
    """
    CREATE TABLE IF NOT EXISTS graph_neighborhoods (
        center_node_id TEXT NOT NULL,
        neighbor_node_id TEXT NOT NULL,
        distance INTEGER NOT NULL CHECK (distance >= 1),
        connecting_path_json TEXT NOT NULL
            CHECK (json_valid(connecting_path_json) AND json_type(connecting_path_json) = 'array'),
        edge_types_json TEXT NOT NULL
            CHECK (json_valid(edge_types_json) AND json_type(edge_types_json) = 'array'),
        relationship_summary TEXT NOT NULL DEFAULT '',
        neighbor_score REAL NOT NULL DEFAULT 0.0,
        PRIMARY KEY (center_node_id, neighbor_node_id, distance),
        CHECK (center_node_id <> neighbor_node_id),
        FOREIGN KEY (center_node_id) REFERENCES graph_nodes(node_id),
        FOREIGN KEY (neighbor_node_id) REFERENCES graph_nodes(node_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_neighborhood_center ON graph_neighborhoods(center_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_neighborhood_neighbor ON graph_neighborhoods(neighbor_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_neighborhood_distance ON graph_neighborhoods(distance)",
    "CREATE INDEX IF NOT EXISTS idx_neighborhood_center_distance_score ON graph_neighborhoods(center_node_id, distance, neighbor_score DESC)",
    """
    CREATE TABLE IF NOT EXISTS resume_metric_usage (
        run_id TEXT NOT NULL CHECK (TRIM(run_id) <> ''),
        resume_section TEXT NOT NULL CHECK (TRIM(resume_section) <> ''),
        metric_id TEXT NOT NULL CHECK (TRIM(metric_id) <> ''),
        metric_value TEXT NOT NULL DEFAULT '',
        fact_id TEXT NOT NULL DEFAULT '',
        skill_id TEXT NOT NULL DEFAULT '',
        role_family_key TEXT NOT NULL DEFAULT '',
        usage_count INTEGER NOT NULL DEFAULT 1 CHECK (usage_count >= 1),
        created_at TEXT NOT NULL,
        PRIMARY KEY (run_id, resume_section, metric_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_metric ON resume_metric_usage(metric_id)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_section ON resume_metric_usage(resume_section)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_fact ON resume_metric_usage(fact_id)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_skill ON resume_metric_usage(skill_id)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_role ON resume_metric_usage(role_family_key)",
    "CREATE INDEX IF NOT EXISTS idx_metric_usage_metric_section ON resume_metric_usage(metric_id, resume_section)",
    """
    CREATE TABLE IF NOT EXISTS section_evidence_budget (
        section_id TEXT NOT NULL CHECK (TRIM(section_id) <> ''),
        role_family_key TEXT NOT NULL CHECK (TRIM(role_family_key) <> ''),
        max_metric_reuse INTEGER NOT NULL DEFAULT 1 CHECK (max_metric_reuse >= 0),
        max_fact_family_reuse INTEGER NOT NULL DEFAULT 2 CHECK (max_fact_family_reuse >= 0),
        required_node_types_json TEXT NOT NULL DEFAULT '[]'
            CHECK (json_valid(required_node_types_json) AND json_type(required_node_types_json) = 'array'),
        preferred_edge_types_json TEXT NOT NULL DEFAULT '[]'
            CHECK (json_valid(preferred_edge_types_json) AND json_type(preferred_edge_types_json) = 'array'),
        forbidden_metric_ids_json TEXT NOT NULL DEFAULT '[]'
            CHECK (json_valid(forbidden_metric_ids_json) AND json_type(forbidden_metric_ids_json) = 'array'),
        preferred_metric_families_json TEXT NOT NULL DEFAULT '[]'
            CHECK (json_valid(preferred_metric_families_json) AND json_type(preferred_metric_families_json) = 'array'),
        PRIMARY KEY (section_id, role_family_key)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS graph_selection_rejections (
        run_id TEXT NOT NULL CHECK (TRIM(run_id) <> ''),
        section_id TEXT NOT NULL CHECK (TRIM(section_id) <> ''),
        candidate_node_id TEXT NOT NULL CHECK (TRIM(candidate_node_id) <> ''),
        candidate_node_type TEXT NOT NULL CHECK (TRIM(candidate_node_type) <> ''),
        rejected_reason TEXT NOT NULL CHECK (TRIM(rejected_reason) <> ''),
        rejected_at_stage TEXT NOT NULL CHECK (TRIM(rejected_at_stage) <> ''),
        competing_selected_node_id TEXT NOT NULL DEFAULT '',
        path_signature TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        PRIMARY KEY (run_id, section_id, candidate_node_id, rejected_at_stage)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_rejections_run_section ON graph_selection_rejections(run_id, section_id)",
    "CREATE INDEX IF NOT EXISTS idx_rejections_candidate ON graph_selection_rejections(candidate_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_graph_edges_src_type_tgt ON graph_edges(source_node_id, edge_type, target_node_id)",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_graph_edges_src_tgt_type ON graph_edges(source_node_id, target_node_id, edge_type)",
)

GRAPHDB_CAPABILITY_TABLE_COLUMNS: dict[str, frozenset[str]] = {
    "graph_paths": frozenset(
        {
            "path_id",
            "start_node_id",
            "end_node_id",
            "path_depth",
            "path_signature",
            "node_path_json",
            "edge_path_json",
            "edge_types_json",
            "proof_fact_ids_json",
            "metric_ids_json",
            "section_ids_json",
            "path_score",
            "novelty_score",
            "proof_strength_score",
            "created_at",
        }
    ),
    "graph_sibling_links": frozenset(
        {
            "node_id",
            "sibling_node_id",
            "sibling_reason",
            "shared_parent_node_id",
            "shared_edge_type",
            "sibling_score",
        }
    ),
    "graph_neighborhoods": frozenset(
        {
            "center_node_id",
            "neighbor_node_id",
            "distance",
            "connecting_path_json",
            "edge_types_json",
            "relationship_summary",
            "neighbor_score",
        }
    ),
    "resume_metric_usage": frozenset(
        {
            "run_id",
            "resume_section",
            "metric_id",
            "metric_value",
            "fact_id",
            "skill_id",
            "role_family_key",
            "usage_count",
            "created_at",
        }
    ),
    "section_evidence_budget": frozenset(
        {
            "section_id",
            "role_family_key",
            "max_metric_reuse",
            "max_fact_family_reuse",
            "required_node_types_json",
            "preferred_edge_types_json",
            "forbidden_metric_ids_json",
            "preferred_metric_families_json",
        }
    ),
    "graph_selection_rejections": frozenset(
        {
            "run_id",
            "section_id",
            "candidate_node_id",
            "candidate_node_type",
            "rejected_reason",
            "rejected_at_stage",
            "competing_selected_node_id",
            "path_signature",
            "created_at",
        }
    ),
}

GRAPHDB_CAPABILITY_INDEXES = frozenset(
    {
        "idx_graph_paths_start",
        "idx_graph_paths_end",
        "idx_graph_paths_depth",
        "idx_graph_paths_end_depth_score",
        "idx_sibling_node",
        "idx_sibling_peer",
        "idx_sibling_node_score",
        "idx_sibling_context_lookup",
        "idx_neighborhood_center",
        "idx_neighborhood_neighbor",
        "idx_neighborhood_distance",
        "idx_neighborhood_center_distance_score",
        "idx_metric_usage_metric",
        "idx_metric_usage_section",
        "idx_metric_usage_fact",
        "idx_metric_usage_skill",
        "idx_metric_usage_role",
        "idx_metric_usage_metric_section",
        "idx_rejections_run_section",
        "idx_rejections_candidate",
        "idx_graph_edges_src_type_tgt",
        "uq_graph_edges_src_tgt_type",
    }
)

REQUIRED_FOREIGN_KEYS: dict[str, frozenset[tuple[str, str, str]]] = {
    "graph_edges": frozenset(
        {
            ("source_node_id", "graph_nodes", "node_id"),
            ("target_node_id", "graph_nodes", "node_id"),
        }
    ),
    "skill_fact_links": frozenset(
        {
            ("skill_id", "graph_nodes", "node_id"),
            ("fact_id", "graph_nodes", "node_id"),
        }
    ),
    "graph_paths": frozenset(
        {
            ("start_node_id", "graph_nodes", "node_id"),
            ("end_node_id", "graph_nodes", "node_id"),
        }
    ),
    "graph_sibling_links": frozenset(
        {
            ("node_id", "graph_nodes", "node_id"),
            ("sibling_node_id", "graph_nodes", "node_id"),
            ("shared_parent_node_id", "graph_nodes", "node_id"),
        }
    ),
    "graph_neighborhoods": frozenset(
        {
            ("center_node_id", "graph_nodes", "node_id"),
            ("neighbor_node_id", "graph_nodes", "node_id"),
        }
    ),
}

REQUIRED_PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "graph_sibling_links": (
        "node_id",
        "sibling_node_id",
        "shared_parent_node_id",
        "shared_edge_type",
    ),
}

REQUIRED_CHECK_FRAGMENTS: dict[str, tuple[str, ...]] = {
    "graph_nodes": ("check(trim(node_id)<>'')",),
    "graph_edges": (
        "check(trim(edge_id)<>'')",
        "check(weight>=0.0andweight<=1.0)",
        "check(directionalin(0,1))",
    ),
    "skill_fact_links": (
        "check(claim_eligibilityin(0,1))",
        "check(human_confirmedin(0,1))",
        "check(external_eligiblein(0,1))",
    ),
    "graph_paths": (
        "check(path_depth>=1)",
        "check(json_valid(node_path_json)andjson_type(node_path_json)='array')",
        "check(json_valid(edge_path_json)andjson_type(edge_path_json)='array')",
        "check(json_valid(edge_types_json)andjson_type(edge_types_json)='array')",
    ),
    "graph_sibling_links": ("check(node_id<>sibling_node_id)",),
    "graph_neighborhoods": (
        "check(distance>=1)",
        "check(center_node_id<>neighbor_node_id)",
        "check(json_valid(connecting_path_json)andjson_type(connecting_path_json)='array')",
        "check(json_valid(edge_types_json)andjson_type(edge_types_json)='array')",
    ),
}

REQUIRED_INDEX_DEFINITIONS: dict[str, tuple[tuple[str, ...], bool]] = {
    "idx_graph_edges_src_type_tgt": (("source_node_id", "edge_type", "target_node_id"), False),
    "uq_graph_edges_src_tgt_type": (("source_node_id", "target_node_id", "edge_type"), True),
    "idx_graph_paths_end_depth_score": (("end_node_id", "path_depth", "path_score"), False),
    "idx_sibling_node_score": (("node_id", "sibling_score"), False),
    "idx_sibling_context_lookup": (
        (
            "node_id",
            "sibling_node_id",
            "shared_parent_node_id",
            "shared_edge_type",
        ),
        False,
    ),
    "idx_neighborhood_center_distance_score": (("center_node_id", "distance", "neighbor_score"), False),
}

GRAPHDB_REVERSE_VIEW_COLUMNS = frozenset(
    {
        "edge_id",
        "source_node_id",
        "target_node_id",
        "edge_type",
        "edge_family",
        "weight",
        "confidence",
        "evidence_status",
        "section_fit",
        "source_authority",
        "rationale",
        "projection_behavior",
        "external_claim_policy",
        "validation_status",
        "edge_note",
        "operator_note",
        "business_story",
        "technical_story",
    }
)

METRIC_NODE_TYPES = frozenset({"metric", "metric_bucket", "metric_outcome"})
HIGH_VALUE_NODE_TYPES = frozenset(
    {"role_family", "career_track", "pillar", "skill", "fact", "section", *METRIC_NODE_TYPES}
)
SIBLING_NODE_TYPES = frozenset({"skill", "fact", *METRIC_NODE_TYPES})
SKILL_FACT_EVIDENCE_NODE_TYPES = frozenset({"fact", "locked_bullet", "employment", "certification"})


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


def _schema_object_type(conn: sqlite3.Connection, object_name: str) -> str | None:
    row = conn.execute(
        "SELECT type FROM sqlite_master WHERE name = ? LIMIT 1",
        (object_name,),
    ).fetchone()
    return str(row[0]) if row else None


def _node_type_map(conn: sqlite3.Connection) -> dict[str, str]:
    if not table_exists(conn, "graph_nodes"):
        return {}
    return {
        str(node_id): str(node_type)
        for node_id, node_type in conn.execute("SELECT node_id, node_type FROM graph_nodes")
    }


def _normalized_schema_sql(conn: sqlite3.Connection, object_name: str) -> str:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name = ? LIMIT 1",
        (object_name,),
    ).fetchone()
    return "" if not row or not row[0] else "".join(str(row[0]).lower().split())


def _foreign_key_mappings(conn: sqlite3.Connection, table_name: str) -> frozenset[tuple[str, str, str]]:
    return frozenset(
        (str(row[3]), str(row[2]), str(row[4]))
        for row in conn.execute(f"PRAGMA foreign_key_list({table_name})")
    )


def _primary_key_columns(conn: sqlite3.Connection, table_name: str) -> tuple[str, ...]:
    keyed_columns = [
        (int(row[5]), str(row[1])) for row in conn.execute(f"PRAGMA table_info({table_name})") if int(row[5])
    ]
    return tuple(column for _position, column in sorted(keyed_columns))


def _index_definition(conn: sqlite3.Connection, index_name: str) -> tuple[tuple[str, ...], bool] | None:
    index_rows = conn.execute("PRAGMA index_list(graph_edges)").fetchall()
    table_row = conn.execute(
        "SELECT tbl_name FROM sqlite_master WHERE type='index' AND name=?",
        (index_name,),
    ).fetchone()
    if not table_row:
        return None
    table_name = str(table_row[0])
    if table_name != "graph_edges":
        index_rows = conn.execute(f"PRAGMA index_list({table_name})").fetchall()
    unique = next(
        (bool(row[2]) for row in index_rows if str(row[1]) == index_name),
        False,
    )
    columns = tuple(str(row[2]) for row in conn.execute(f"PRAGMA index_info({index_name})").fetchall())
    return columns, unique


def _schema_assertion_issues(
    conn: sqlite3.Connection,
    *,
    include_capability_tables: bool,
) -> list[str]:
    issues: list[str] = []
    tables = {"graph_nodes", "graph_edges", "skill_fact_links"}
    if include_capability_tables:
        tables.update(GRAPHDB_CAPABILITY_TABLE_COLUMNS)
    for table_name in sorted(tables):
        if _schema_object_type(conn, table_name) != "table":
            continue
        schema_sql = _normalized_schema_sql(conn, table_name)
        for fragment in REQUIRED_CHECK_FRAGMENTS.get(table_name, ()):
            if fragment not in schema_sql:
                issues.append(f"{table_name} missing CHECK assertion: {fragment}")
        expected_fks = REQUIRED_FOREIGN_KEYS.get(table_name, frozenset())
        if expected_fks:
            actual_fks = _foreign_key_mappings(conn, table_name)
            missing_fks = sorted(expected_fks - actual_fks)
            if missing_fks:
                issues.append(f"{table_name} missing foreign keys: {missing_fks!r}")
        expected_primary_key = REQUIRED_PRIMARY_KEYS.get(table_name)
        if expected_primary_key:
            actual_primary_key = _primary_key_columns(conn, table_name)
            if actual_primary_key != expected_primary_key:
                issues.append(
                    f"{table_name} primary key mismatch: "
                    f"expected={expected_primary_key!r} actual={actual_primary_key!r}"
                )
    if include_capability_tables:
        for index_name, expected in REQUIRED_INDEX_DEFINITIONS.items():
            actual = _index_definition(conn, index_name)
            if actual != expected:
                issues.append(
                    f"index definition mismatch: {index_name} expected={expected!r} actual={actual!r}"
                )
    return issues


_GRAPH_DIGEST_COLUMNS: dict[str, tuple[str, ...]] = {
    "graph_nodes": (
        "node_id",
        "node_type",
        "label",
        "description",
        "activation_status",
        "support_level",
        "confidence",
        "external_eligible",
        "source_authority",
    ),
    "graph_edges": (
        "edge_id",
        "source_node_id",
        "target_node_id",
        "edge_family",
        "edge_type",
        "weight",
        "confidence",
        "directional",
        "evidence_status",
        "section_fit",
        "source_authority",
        "rationale",
        "projection_behavior",
        "external_claim_policy",
        "validation_status",
        "edge_note",
        "operator_note",
        "business_story",
        "technical_story",
    ),
    "skill_fact_links": (
        "skill_id",
        "fact_id",
        "support_level",
        "claim_eligibility",
        "source_trace",
        "archive_trace",
        "human_confirmed",
        "external_eligible",
    ),
    "section_eligibility": (
        "node_id",
        "section_id",
        "allowed",
        "claim_policy",
        "reason",
        "blocked_reason",
    ),
    "role_family_projection": (
        "role_family_id",
        "projection_role_family_key",
        "track_weight_profile",
        "taxonomy_source",
        "targeting_keywords",
        "proof_policy_note",
    ),
    "c03_skill_selection_features": (
        "skill_id",
        "pillar",
        "subpillar",
        "domain_id",
        "career_track_id",
        "skill_family",
        "metric_bucket",
        "role_family_weights",
        "allowed_sections",
        "source_fact_count",
        "confidence",
        "activation_status",
        "support_level",
        "external_eligible",
        "source_authority",
        "source_trace",
    ),
    "c03_role_family_skill_weights": (
        "skill_id",
        "role_family_key",
        "weight",
        "source",
    ),
    "graph_paths": (
        "path_id",
        "start_node_id",
        "end_node_id",
        "path_depth",
        "path_signature",
        "node_path_json",
        "edge_path_json",
        "edge_types_json",
        "proof_fact_ids_json",
        "metric_ids_json",
        "section_ids_json",
        "path_score",
        "novelty_score",
        "proof_strength_score",
    ),
    "graph_neighborhoods": (
        "center_node_id",
        "neighbor_node_id",
        "distance",
        "connecting_path_json",
        "edge_types_json",
        "relationship_summary",
        "neighbor_score",
    ),
    "graph_sibling_links": (
        "node_id",
        "sibling_node_id",
        "sibling_reason",
        "shared_parent_node_id",
        "shared_edge_type",
        "sibling_score",
    ),
    "section_evidence_budget": (
        "section_id",
        "role_family_key",
        "max_metric_reuse",
        "max_fact_family_reuse",
        "required_node_types_json",
        "preferred_edge_types_json",
        "forbidden_metric_ids_json",
        "preferred_metric_families_json",
    ),
}


def _canonical_sqlite_digest_value(value: Any) -> dict[str, str | None]:
    """Encode SQLite storage classes without Python cross-type comparisons."""
    if value is None:
        return {"type": "null", "value": None}
    if isinstance(value, bool):
        return {"type": "integer", "value": "1" if value else "0"}
    if isinstance(value, int):
        return {"type": "integer", "value": str(value)}
    if isinstance(value, float):
        return {"type": "real", "value": value.hex()}
    if isinstance(value, str):
        return {"type": "text", "value": value}
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"type": "blob", "value": bytes(value).hex()}
    raise ValueError(f"unsupported SQLite value type: {type(value).__name__}")


def compute_sqlite_graph_digest(conn: sqlite3.Connection) -> str:
    """Digest immutable and ranking-relevant rows, excluding runtime memory."""
    payload: dict[str, list[list[dict[str, str | None]]]] = {}
    for table_name, columns in _GRAPH_DIGEST_COLUMNS.items():
        if _schema_object_type(conn, table_name) != "table":
            raise ValueError(f"cannot digest missing graph table: {table_name}")
        missing = set(columns) - table_columns(conn, table_name)
        if missing:
            raise ValueError(f"cannot digest {table_name}; missing columns: {sorted(missing)!r}")
        rows = conn.execute(f"SELECT {','.join(columns)} FROM {table_name}").fetchall()
        canonical_rows: list[list[dict[str, str | None]]] = []
        for row in rows:
            canonical_row: list[dict[str, str | None]] = []
            for column_name, value in zip(columns, row, strict=True):
                try:
                    canonical_row.append(_canonical_sqlite_digest_value(value))
                except ValueError as exc:
                    raise ValueError(
                        f"cannot digest unsupported SQLite value: table={table_name} column={column_name}"
                    ) from exc
            canonical_rows.append(canonical_row)
        payload[table_name] = sorted(canonical_rows, key=_json)
    return _digest(_json(payload))


def compute_sqlite_schema_digest(conn: sqlite3.Connection) -> str:
    """Digest every user-defined table, index, view, and trigger definition."""
    rows = conn.execute(
        """
        SELECT type,name,tbl_name,COALESCE(sql,'')
        FROM sqlite_master
        WHERE type IN ('table','index','view','trigger')
          AND name NOT LIKE 'sqlite_%'
        ORDER BY type,name,tbl_name
        """
    ).fetchall()
    payload = [
        {
            "type": str(object_type),
            "name": str(name),
            "table_name": str(table_name),
            "sql": " ".join(str(sql or "").split()),
        }
        for object_type, name, table_name, sql in rows
    ]
    return _digest(_json(payload))


def require_graphdb_capability_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    """Inspect the graphDB projection schema without mutating connection or storage state."""
    issues: list[str] = []
    for source_table in ("graph_nodes", "skill_fact_links"):
        if _schema_object_type(conn, source_table) != "table":
            issues.append(f"missing source table: {source_table}")
    if _schema_object_type(conn, "graph_edges") != "table":
        issues.append("missing table: graph_edges")
    else:
        missing_edge_columns = sorted(
            {column for column, _ddl in EDGE_METADATA_COLUMNS} - table_columns(conn, "graph_edges")
        )
        if missing_edge_columns:
            issues.append("graph_edges missing columns: " + ",".join(missing_edge_columns))

    present_tables: list[str] = []
    for table_name, required_columns in GRAPHDB_CAPABILITY_TABLE_COLUMNS.items():
        if _schema_object_type(conn, table_name) != "table":
            issues.append(f"missing table: {table_name}")
            continue
        present_tables.append(table_name)
        missing_columns = sorted(required_columns - table_columns(conn, table_name))
        if missing_columns:
            issues.append(f"{table_name} missing columns: " + ",".join(missing_columns))

    reverse_view_exists = _schema_object_type(conn, "graph_edges_reverse") == "view"
    if not reverse_view_exists:
        issues.append("missing view: graph_edges_reverse")
    else:
        missing_reverse_columns = sorted(
            GRAPHDB_REVERSE_VIEW_COLUMNS - table_columns(conn, "graph_edges_reverse")
        )
        if missing_reverse_columns:
            issues.append("graph_edges_reverse missing columns: " + ",".join(missing_reverse_columns))

    present_indexes = {
        str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()
    }
    missing_indexes = sorted(GRAPHDB_CAPABILITY_INDEXES - present_indexes)
    if missing_indexes:
        issues.append("missing indexes: " + ",".join(missing_indexes))
    issues.extend(_schema_assertion_issues(conn, include_capability_tables=True))

    if issues:
        raise ValueError("graphDB capability schema incomplete: " + "; ".join(issues))
    return {
        "schema_status": "GRAPHDB_CAPABILITY_SCHEMA_READY",
        "graph_index_schema_version": GRAPH_INDEX_SCHEMA_VERSION,
        "added_graph_edges_columns": [],
        "tables": sorted(present_tables),
        "reverse_view_exists": reverse_view_exists,
    }


def ensure_graphdb_capability_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    """Explicitly install additive graphDB schema; never drops source rows."""
    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON")
    if int(conn.execute("PRAGMA foreign_keys").fetchone()[0]) != 1:
        raise RuntimeError("SQLite foreign key enforcement could not be enabled for schema writes")
    source_schema_issues = _schema_assertion_issues(conn, include_capability_tables=False)
    if source_schema_issues:
        raise ValueError(
            "legacy graph schema requires the explicit atomic applicator: " + "; ".join(source_schema_issues)
        )
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
    result = require_graphdb_capability_schema(conn)
    result["added_graph_edges_columns"] = added_columns
    return result


def validate_graphdb_capability_integrity(
    conn: sqlite3.Connection,
    *,
    expected_materializer_version: str | None = None,
) -> dict[str, Any]:
    """Run read-only SQLite, FK, JSON, and cross-row integrity assertions."""
    require_graphdb_capability_schema(conn)
    integrity_rows = [str(row[0]) for row in conn.execute("PRAGMA integrity_check")]
    foreign_key_rows = [tuple(row) for row in conn.execute("PRAGMA foreign_key_check")]
    evidence_node_types_sql = ",".join(
        f"'{node_type}'" for node_type in sorted(SKILL_FACT_EVIDENCE_NODE_TYPES)
    )
    sibling_node_types_sql = ",".join(f"'{node_type}'" for node_type in sorted(SIBLING_NODE_TYPES))
    checks = {
        "duplicate_graph_edge_triples": """
            SELECT COUNT(*) FROM (
                SELECT source_node_id, target_node_id, edge_type
                FROM graph_edges
                GROUP BY source_node_id, target_node_id, edge_type
                HAVING COUNT(*) > 1
            )
        """,
        "broken_graph_edges": """
            SELECT COUNT(*) FROM graph_edges e
            LEFT JOIN graph_nodes s ON s.node_id = e.source_node_id
            LEFT JOIN graph_nodes t ON t.node_id = e.target_node_id
            WHERE s.node_id IS NULL OR t.node_id IS NULL
        """,
        "invalid_graph_edge_weights": """
            SELECT COUNT(*) FROM graph_edges
            WHERE weight < 0.0 OR weight > 1.0
        """,
        "broken_skill_fact_links": f"""
            SELECT COUNT(*) FROM skill_fact_links l
            LEFT JOIN graph_nodes s ON s.node_id = l.skill_id
            LEFT JOIN graph_nodes f ON f.node_id = l.fact_id
            WHERE s.node_id IS NULL OR s.node_type <> 'skill'
               OR f.node_id IS NULL
               OR f.node_type NOT IN ({evidence_node_types_sql})
        """,
        "broken_graph_paths": """
            SELECT COUNT(*) FROM graph_paths p
            LEFT JOIN graph_nodes s ON s.node_id = p.start_node_id
            LEFT JOIN graph_nodes e ON e.node_id = p.end_node_id
            WHERE s.node_id IS NULL OR e.node_id IS NULL
        """,
        "malformed_graph_paths": """
            SELECT COUNT(*) FROM graph_paths
            WHERE CASE
                WHEN json_valid(node_path_json)
                 AND json_type(node_path_json) = 'array'
                 AND json_valid(edge_path_json)
                 AND json_type(edge_path_json) = 'array'
                 AND json_valid(edge_types_json)
                 AND json_type(edge_types_json) = 'array'
                THEN path_depth < 1
                  OR json_array_length(node_path_json) <> path_depth + 1
                  OR json_array_length(edge_path_json) <> path_depth
                  OR json_array_length(edge_types_json) <> path_depth
                ELSE 1
            END
        """,
        "graph_path_endpoint_mismatches": """
            SELECT COUNT(*) FROM graph_paths
            WHERE CASE
                WHEN json_valid(node_path_json)
                 AND json_type(node_path_json) = 'array'
                THEN json_extract(node_path_json, '$[0]') <> start_node_id
                  OR json_extract(node_path_json, '$[#-1]') <> end_node_id
                ELSE 0
            END
        """,
        "broken_graph_path_edge_refs": """
            SELECT COUNT(*) FROM graph_paths p
            JOIN json_each(
                CASE WHEN json_valid(p.edge_path_json)
                     THEN p.edge_path_json ELSE '[]' END
            ) j
            LEFT JOIN graph_edges e ON e.edge_id = j.value
            WHERE e.edge_id IS NULL
        """,
        "graph_path_edge_continuity_mismatches": """
            SELECT COUNT(*) FROM graph_paths p
            JOIN json_each(
                CASE WHEN json_valid(p.edge_path_json)
                     THEN p.edge_path_json ELSE '[]' END
            ) j
            JOIN graph_edges e ON e.edge_id = j.value
            WHERE e.source_node_id IS NOT json_extract(
                      CASE WHEN json_valid(p.node_path_json)
                           THEN p.node_path_json ELSE '[]' END,
                      '$[' || j.key || ']'
                  )
               OR e.target_node_id IS NOT json_extract(
                      CASE WHEN json_valid(p.node_path_json)
                           THEN p.node_path_json ELSE '[]' END,
                      '$[' || (j.key + 1) || ']'
                  )
        """,
        "graph_path_edge_type_mismatches": """
            SELECT COUNT(*) FROM graph_paths p
            JOIN json_each(
                CASE WHEN json_valid(p.edge_path_json)
                     THEN p.edge_path_json ELSE '[]' END
            ) j
            JOIN graph_edges e ON e.edge_id = j.value
            WHERE e.edge_type IS NOT json_extract(
                CASE WHEN json_valid(p.edge_types_json)
                     THEN p.edge_types_json ELSE '[]' END,
                '$[' || j.key || ']'
            )
        """,
        "graph_edge_depth1_path_identity_mismatches": """
            SELECT COUNT(*) FROM (
                SELECT e.edge_id
                FROM graph_edges e
                LEFT JOIN graph_paths p
                  ON p.path_depth = 1
                 AND p.start_node_id = e.source_node_id
                 AND p.end_node_id = e.target_node_id
                 AND json_array_length(
                     CASE WHEN json_valid(p.edge_path_json)
                          THEN p.edge_path_json ELSE '[]' END
                 ) = 1
                 AND json_extract(
                     CASE WHEN json_valid(p.edge_path_json)
                          THEN p.edge_path_json ELSE '[]' END,
                     '$[0]'
                 ) IS e.edge_id
                GROUP BY e.edge_id
                HAVING COUNT(p.path_id) <> 1
            )
        """,
        "broken_graph_sibling_links": """
            SELECT COUNT(*) FROM graph_sibling_links g
            LEFT JOIN graph_nodes n ON n.node_id = g.node_id
            LEFT JOIN graph_nodes s ON s.node_id = g.sibling_node_id
            LEFT JOIN graph_nodes p ON p.node_id = g.shared_parent_node_id
            WHERE n.node_id IS NULL OR s.node_id IS NULL
               OR g.node_id = g.sibling_node_id
               OR (g.shared_parent_node_id <> '' AND p.node_id IS NULL)
        """,
        "nonreciprocal_graph_sibling_links": """
            SELECT COUNT(*) FROM graph_sibling_links g
            LEFT JOIN graph_sibling_links r
             ON r.node_id = g.sibling_node_id
             AND r.sibling_node_id = g.node_id
             AND r.shared_parent_node_id = g.shared_parent_node_id
             AND r.shared_edge_type = g.shared_edge_type
            WHERE r.node_id IS NULL
        """,
        "broken_graph_sibling_parent_edges": """
            SELECT COUNT(*) FROM graph_sibling_links g
            LEFT JOIN graph_edges n
              ON n.source_node_id = g.shared_parent_node_id
             AND n.target_node_id = g.node_id
             AND n.edge_type = g.shared_edge_type
            LEFT JOIN graph_edges s
              ON s.source_node_id = g.shared_parent_node_id
             AND s.target_node_id = g.sibling_node_id
             AND s.edge_type = g.shared_edge_type
            WHERE g.shared_parent_node_id <> ''
              AND (n.edge_id IS NULL OR s.edge_id IS NULL)
        """,
        "graph_sibling_context_set_mismatches": f"""
            WITH sanctioned_children AS (
                SELECT e.source_node_id AS parent_node_id,
                       e.edge_type,
                       e.target_node_id AS child_node_id
                FROM graph_edges e
                JOIN graph_nodes n ON n.node_id = e.target_node_id
                WHERE n.node_type IN ({sibling_node_types_sql})
            ),
            expected AS (
                SELECT a.child_node_id AS node_id,
                       b.child_node_id AS sibling_node_id,
                       a.parent_node_id AS shared_parent_node_id,
                       a.edge_type AS shared_edge_type
                FROM sanctioned_children a
                JOIN sanctioned_children b
                  ON b.parent_node_id = a.parent_node_id
                 AND b.edge_type = a.edge_type
                 AND b.child_node_id <> a.child_node_id
            )
            SELECT
                (SELECT COUNT(*) FROM (
                    SELECT e.node_id, e.sibling_node_id,
                           e.shared_parent_node_id, e.shared_edge_type
                    FROM expected e
                    LEFT JOIN graph_sibling_links g
                      ON g.node_id = e.node_id
                     AND g.sibling_node_id = e.sibling_node_id
                     AND g.shared_parent_node_id = e.shared_parent_node_id
                     AND g.shared_edge_type = e.shared_edge_type
                    GROUP BY e.node_id, e.sibling_node_id,
                             e.shared_parent_node_id, e.shared_edge_type
                    HAVING COUNT(g.rowid) <> 1
                ))
                +
                (SELECT COUNT(*)
                 FROM graph_sibling_links g
                 LEFT JOIN expected e
                   ON e.node_id = g.node_id
                  AND e.sibling_node_id = g.sibling_node_id
                  AND e.shared_parent_node_id = g.shared_parent_node_id
                  AND e.shared_edge_type = g.shared_edge_type
                 WHERE e.node_id IS NULL)
        """,
        "broken_graph_neighborhoods": """
            SELECT COUNT(*) FROM graph_neighborhoods g
            LEFT JOIN graph_nodes c ON c.node_id = g.center_node_id
            LEFT JOIN graph_nodes n ON n.node_id = g.neighbor_node_id
            WHERE c.node_id IS NULL OR n.node_id IS NULL
               OR g.center_node_id = g.neighbor_node_id
        """,
        "malformed_graph_neighborhoods": """
            SELECT COUNT(*) FROM graph_neighborhoods
            WHERE CASE
                WHEN json_valid(connecting_path_json)
                 AND json_type(connecting_path_json) = 'array'
                 AND json_valid(edge_types_json)
                 AND json_type(edge_types_json) = 'array'
                THEN distance < 1
                  OR json_array_length(connecting_path_json) <> distance + 1
                  OR json_array_length(edge_types_json) <> distance
                ELSE 1
            END
        """,
        "graph_neighborhood_endpoint_mismatches": """
            SELECT COUNT(*) FROM graph_neighborhoods
            WHERE CASE
                WHEN json_valid(connecting_path_json)
                 AND json_type(connecting_path_json) = 'array'
                THEN json_extract(connecting_path_json, '$[0]') <> center_node_id
                  OR json_extract(connecting_path_json, '$[#-1]') <> neighbor_node_id
                ELSE 0
            END
        """,
        "graph_neighborhood_hop_continuity_mismatches": """
            SELECT COUNT(*) FROM graph_neighborhoods g
            JOIN json_each(
                CASE WHEN json_valid(g.edge_types_json)
                     THEN g.edge_types_json ELSE '[]' END
            ) j
            WHERE NOT EXISTS (
                SELECT 1 FROM graph_edges e
                WHERE (
                    e.source_node_id IS json_extract(
                        CASE WHEN json_valid(g.connecting_path_json)
                             THEN g.connecting_path_json ELSE '[]' END,
                        '$[' || j.key || ']'
                    )
                    AND e.target_node_id IS json_extract(
                        CASE WHEN json_valid(g.connecting_path_json)
                             THEN g.connecting_path_json ELSE '[]' END,
                        '$[' || (j.key + 1) || ']'
                    )
                    AND e.edge_type IS j.value
                ) OR (
                    e.target_node_id IS json_extract(
                        CASE WHEN json_valid(g.connecting_path_json)
                             THEN g.connecting_path_json ELSE '[]' END,
                        '$[' || j.key || ']'
                    )
                    AND e.source_node_id IS json_extract(
                        CASE WHEN json_valid(g.connecting_path_json)
                             THEN g.connecting_path_json ELSE '[]' END,
                        '$[' || (j.key + 1) || ']'
                    )
                    AND e.edge_type || '_reverse' IS j.value
                )
            )
        """,
        "graph_edge_distance1_neighborhood_mismatches": """
            WITH expected(center_node_id, neighbor_node_id) AS (
                SELECT source_node_id, target_node_id
                FROM graph_edges
                WHERE source_node_id <> target_node_id
                UNION
                SELECT target_node_id, source_node_id
                FROM graph_edges
                WHERE source_node_id <> target_node_id
            )
            SELECT COUNT(*) FROM (
                SELECT e.center_node_id, e.neighbor_node_id
                FROM expected e
                LEFT JOIN graph_neighborhoods g
                  ON g.center_node_id = e.center_node_id
                 AND g.neighbor_node_id = e.neighbor_node_id
                 AND g.distance = 1
                GROUP BY e.center_node_id, e.neighbor_node_id
                HAVING COUNT(g.rowid) <> 1
            )
        """,
        "reverse_view_multiset_mismatches": """
            SELECT
                (SELECT ABS(
                    (SELECT COUNT(*) FROM graph_edges)
                    - (SELECT COUNT(*) FROM graph_edges_reverse)
                ))
                + (SELECT COUNT(*) FROM graph_edges e
                   LEFT JOIN graph_edges_reverse r
                     ON r.edge_id IS e.edge_id
                    AND r.source_node_id IS e.target_node_id
                    AND r.target_node_id IS e.source_node_id
                    AND r.edge_type IS e.edge_type || '_reverse'
                    AND r.edge_family IS e.edge_family
                    AND r.weight IS e.weight
                    AND r.confidence IS e.confidence
                    AND r.evidence_status IS e.evidence_status
                    AND r.section_fit IS e.section_fit
                    AND r.source_authority IS e.source_authority
                    AND r.rationale IS e.rationale
                    AND r.projection_behavior IS e.projection_behavior
                    AND r.external_claim_policy IS e.external_claim_policy
                    AND r.validation_status IS e.validation_status
                    AND r.edge_note IS e.edge_note
                    AND r.operator_note IS e.operator_note
                    AND r.business_story IS e.business_story
                    AND r.technical_story IS e.technical_story
                   WHERE r.edge_id IS NULL)
                + (SELECT COUNT(*) FROM graph_edges_reverse r
                   LEFT JOIN graph_edges e
                     ON r.edge_id IS e.edge_id
                    AND r.source_node_id IS e.target_node_id
                    AND r.target_node_id IS e.source_node_id
                    AND r.edge_type IS e.edge_type || '_reverse'
                    AND r.edge_family IS e.edge_family
                    AND r.weight IS e.weight
                    AND r.confidence IS e.confidence
                    AND r.evidence_status IS e.evidence_status
                    AND r.section_fit IS e.section_fit
                    AND r.source_authority IS e.source_authority
                    AND r.rationale IS e.rationale
                    AND r.projection_behavior IS e.projection_behavior
                    AND r.external_claim_policy IS e.external_claim_policy
                    AND r.validation_status IS e.validation_status
                    AND r.edge_note IS e.edge_note
                    AND r.operator_note IS e.operator_note
                    AND r.business_story IS e.business_story
                    AND r.technical_story IS e.technical_story
                   WHERE e.edge_id IS NULL)
        """,
        "malformed_section_evidence_budget_json": """
            SELECT COUNT(*) FROM section_evidence_budget
            WHERE CASE
                WHEN json_valid(required_node_types_json)
                 AND json_valid(preferred_edge_types_json)
                 AND json_valid(forbidden_metric_ids_json)
                 AND json_valid(preferred_metric_families_json)
                THEN json_type(required_node_types_json) <> 'array'
                  OR json_type(preferred_edge_types_json) <> 'array'
                  OR json_type(forbidden_metric_ids_json) <> 'array'
                  OR json_type(preferred_metric_families_json) <> 'array'
                ELSE 1
            END
        """,
        "invalid_section_evidence_budgets": """
            SELECT COUNT(*) FROM section_evidence_budget
            WHERE max_metric_reuse < 0 OR max_fact_family_reuse < 0
               OR TRIM(section_id) = '' OR TRIM(role_family_key) = ''
        """,
        "invalid_resume_metric_usage": """
            SELECT COUNT(*) FROM resume_metric_usage
            WHERE usage_count < 1 OR TRIM(run_id) = ''
               OR TRIM(resume_section) = '' OR TRIM(metric_id) = ''
        """,
        "broken_resume_metric_usage_refs": f"""
            SELECT COUNT(*) FROM resume_metric_usage u
            LEFT JOIN graph_nodes f ON f.node_id = u.fact_id
            LEFT JOIN graph_nodes s ON s.node_id = u.skill_id
            WHERE (
                u.fact_id <> ''
                AND (
                    f.node_id IS NULL
                    OR f.node_type NOT IN ({evidence_node_types_sql})
                )
            ) OR (
                u.skill_id <> ''
                AND (s.node_id IS NULL OR s.node_type <> 'skill')
            )
        """,
        "broken_graph_selection_rejection_refs": """
            SELECT COUNT(*) FROM graph_selection_rejections r
            LEFT JOIN graph_nodes c ON c.node_id = r.candidate_node_id
            LEFT JOIN graph_nodes s ON s.node_id = r.competing_selected_node_id
            WHERE c.node_id IS NULL
               OR (r.competing_selected_node_id <> '' AND s.node_id IS NULL)
        """,
        "validated_edges_missing_rationale": """
            SELECT COUNT(*) FROM graph_edges
            WHERE LOWER(validation_status) = 'validated'
              AND TRIM(COALESCE(rationale, '')) = ''
        """,
    }
    if table_exists(conn, "section_eligibility"):
        checks["broken_section_eligibility_refs"] = """
            SELECT COUNT(*) FROM section_eligibility e
            LEFT JOIN graph_nodes n ON n.node_id = e.node_id
            WHERE n.node_id IS NULL
        """
    if table_exists(conn, "c03_skill_selection_features"):
        checks["broken_c03_skill_selection_feature_refs"] = """
            SELECT COUNT(*) FROM c03_skill_selection_features f
            LEFT JOIN graph_nodes n ON n.node_id = f.skill_id
            WHERE n.node_id IS NULL OR n.node_type <> 'skill'
        """
    if table_exists(conn, "c03_role_family_skill_weights"):
        checks["broken_c03_role_family_skill_weight_refs"] = """
            SELECT COUNT(*) FROM c03_role_family_skill_weights w
            LEFT JOIN graph_nodes n ON n.node_id = w.skill_id
            WHERE n.node_id IS NULL OR n.node_type <> 'skill'
        """
    cross_row_counts = {name: int(conn.execute(sql).fetchone()[0]) for name, sql in checks.items()}
    from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
        projected_graph_edge_signature_report,
    )

    projected_signature_report = projected_graph_edge_signature_report(
        node_types_by_id=_node_type_map(conn),
        edge_rows=_edge_tuples(conn),
    )
    errors: list[str] = []
    if integrity_rows != ["ok"]:
        errors.append("integrity_check=" + ",".join(integrity_rows))
    if foreign_key_rows:
        errors.append(f"foreign_key_check={len(foreign_key_rows)}")
    errors.extend(f"{name}={count}" for name, count in cross_row_counts.items() if count)
    if projected_signature_report["failure_count"]:
        errors.append(
            "projected_edge_signature_mismatches="
            f"{projected_signature_report['failure_count']} sample="
            f"{_json(projected_signature_report['failure_locators'][:12])}"
        )
    if not table_exists(conn, "graph_metadata"):
        errors.append("graph_metadata_missing=1")
    else:
        metadata_rows = conn.execute(
            "SELECT ledger_hash, graph_count_summary, authority_status FROM graph_metadata"
        ).fetchall()
        if len(metadata_rows) != 1:
            errors.append(f"graph_metadata_row_count={len(metadata_rows)}")
        if metadata_rows:
            ledger_hash, raw_summary, authority_status = metadata_rows[0]
            if not str(ledger_hash or "").strip():
                errors.append("graph_metadata_ledger_hash_empty=1")
            if authority_status != "augmented_skills_graph_authoritative":
                errors.append(f"graph_metadata_authority_status_mismatch={authority_status!r}")
            try:
                metadata_summary = json.loads(raw_summary or "{}")
            except (TypeError, json.JSONDecodeError):
                errors.append("graph_metadata_summary_invalid_json=1")
            else:
                if not isinstance(metadata_summary, dict):
                    errors.append("graph_metadata_summary_not_object=1")
                else:
                    if metadata_summary.get("graph_index_schema_version") != GRAPH_INDEX_SCHEMA_VERSION:
                        errors.append("graph_metadata_schema_version_mismatch=1")
                    if expected_materializer_version and (
                        metadata_summary.get("c03_sqlite_materializer_code_version")
                        != expected_materializer_version
                    ):
                        errors.append("graph_metadata_materializer_version_mismatch=1")
                    if metadata_summary.get("canonical_graph_digest") != ledger_hash:
                        errors.append("graph_metadata_canonical_digest_mismatch=1")
                    try:
                        sqlite_graph_digest = compute_sqlite_graph_digest(conn)
                    except ValueError:
                        errors.append("graph_metadata_sqlite_digest_unavailable=1")
                    else:
                        if metadata_summary.get("sqlite_graph_digest") != sqlite_graph_digest:
                            errors.append("graph_metadata_sqlite_digest_mismatch=1")
                    sqlite_schema_digest = compute_sqlite_schema_digest(conn)
                    if metadata_summary.get("sqlite_schema_digest") != sqlite_schema_digest:
                        errors.append("graph_metadata_sqlite_schema_digest_mismatch=1")
                    expected_counts = {
                        "node_count_sqlite": int(
                            conn.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0]
                        ),
                        "edge_count_sqlite": int(
                            conn.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0]
                        ),
                        "skill_fact_link_count": int(
                            conn.execute("SELECT COUNT(*) FROM skill_fact_links").fetchone()[0]
                        ),
                        "graph_path_count": int(
                            conn.execute("SELECT COUNT(*) FROM graph_paths").fetchone()[0]
                        ),
                        "graph_neighborhood_count": int(
                            conn.execute("SELECT COUNT(*) FROM graph_neighborhoods").fetchone()[0]
                        ),
                        "graph_sibling_link_count": int(
                            conn.execute("SELECT COUNT(*) FROM graph_sibling_links").fetchone()[0]
                        ),
                        "section_evidence_budget_count": int(
                            conn.execute("SELECT COUNT(*) FROM section_evidence_budget").fetchone()[0]
                        ),
                    }
                    for key, expected_count in expected_counts.items():
                        if metadata_summary.get(key) != expected_count:
                            errors.append(
                                f"graph_metadata_count_mismatch:{key}="
                                f"{metadata_summary.get(key)!r}!={expected_count}"
                            )
    if errors:
        raise ValueError("graphDB capability data invalid: " + "; ".join(errors))
    return {
        "status": "GRAPHDB_CAPABILITY_INTEGRITY_PASS",
        "integrity_check": integrity_rows,
        "foreign_key_check": [],
        "cross_row_counts": cross_row_counts,
        "projected_edge_signature_integrity": projected_signature_report,
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
            {col("edge_family")},
            {col("weight", "1.0")},
            {col("confidence")},
            {col("evidence_status")},
            {col("section_fit")},
            {col("source_authority", "'augmented_skills_graph'")},
            {col("rationale")},
            {col("projection_behavior")},
            {col("external_claim_policy")},
            {col("validation_status")},
            {col("edge_note")},
            {col("operator_note")},
            {col("business_story")},
            {col("technical_story")}
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
        facts = [
            node_id for node_id in (src, tgt) if node_types.get(node_id) in SKILL_FACT_EVIDENCE_NODE_TYPES
        ]
        metrics = [node_id for node_id in (src, tgt) if node_types.get(node_id) in METRIC_NODE_TYPES]
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
        if src and tgt and tgt in nodes and node_types.get(tgt) in SIBLING_NODE_TYPES:
            children_by_parent[(src, edge_type)].append(tgt)

    graph_sibling_links: list[dict[str, Any]] = []
    sibling_keys: set[tuple[str, str, str, str]] = set()
    for (parent, edge_type), children in sorted(children_by_parent.items()):
        unique = sorted(set(children))
        if len(unique) < 2:
            continue
        for node_id in unique:
            for sibling_node_id in unique:
                if node_id == sibling_node_id:
                    continue
                key = (node_id, sibling_node_id, parent, edge_type)
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
                    "neighbor_score": round(
                        1.0 + (0.5 if node_types.get(neighbor) in HIGH_VALUE_NODE_TYPES else 0.0), 6
                    ),
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
    """Precompute one direct identity per edge plus deeper high-value paths."""
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

    now = _utc_now()
    direct_paths = build_graph_index_rows(
        node_rows=({"node_id": node_id, "node_type": node_type} for node_id, node_type in node_types.items()),
        edge_rows=edges,
        section_rows=(),
        role_family_projection_rows=(),
        created_at=now,
    )["graph_paths"]
    if len(direct_paths) > max_paths:
        raise ValueError(
            "max_paths cannot preserve one direct graph path per edge: "
            f"required={len(direct_paths)} configured={max_paths}"
        )

    conn.execute("DELETE FROM graph_paths")
    conn.executemany(
        """
        INSERT INTO graph_paths (
            path_id, start_node_id, end_node_id, path_depth, path_signature,
            node_path_json, edge_path_json, edge_types_json, proof_fact_ids_json,
            metric_ids_json, section_ids_json, path_score, novelty_score,
            proof_strength_score, created_at
        ) VALUES (
            :path_id, :start_node_id, :end_node_id, :path_depth, :path_signature,
            :node_path_json, :edge_path_json, :edge_types_json,
            :proof_fact_ids_json, :metric_ids_json, :section_ids_json,
            :path_score, :novelty_score, :proof_strength_score, :created_at
        )
        """,
        direct_paths,
    )
    created = len(direct_paths)
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
                facts = [n for n in new_nodes if node_types.get(n) in SKILL_FACT_EVIDENCE_NODE_TYPES]
                metrics = [n for n in new_nodes if node_types.get(n) in METRIC_NODE_TYPES]
                sections = [
                    n for n in new_nodes if node_types.get(n) == "section" or n.startswith("section_")
                ]
                high_value = bool(facts or metrics or sections or end_type in HIGH_VALUE_NODE_TYPES)
                if high_value and depth >= 2:
                    sig = "->".join(new_nodes)
                    edge_ids = [str(e.get("edge_id") or "") for e in new_edges]
                    path_identity = f"{sig}|{'|'.join(edge_ids)}"
                    path_id = f"path:{_digest(path_identity)[:24]}"
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
                            _json(edge_ids),
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
    persisted = int(conn.execute("SELECT COUNT(*) FROM graph_paths").fetchone()[0])
    return {"graph_paths_materialized": persisted, "max_depth": max_depth}


def build_graph_sibling_links(conn: sqlite3.Connection) -> dict[str, Any]:
    """Build skill/metric/fact sibling links from shared parents."""
    ensure_graphdb_capability_schema(conn)
    node_types = _node_type_map(conn)
    edges = _edge_tuples(conn)
    children_by_parent: dict[tuple[str, str], list[str]] = defaultdict(list)
    for edge in edges:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        et = str(edge.get("edge_type") or "")
        if not src or not tgt:
            continue
        if node_types.get(tgt) in SIBLING_NODE_TYPES:
            children_by_parent[(src, et)].append(tgt)

    conn.execute("DELETE FROM graph_sibling_links")
    inserted = 0
    for (parent, et), children in sorted(children_by_parent.items()):
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
                    INSERT INTO graph_sibling_links (
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
    persisted = int(conn.execute("SELECT COUNT(*) FROM graph_sibling_links").fetchone()[0])
    return {"graph_sibling_links_materialized": persisted}


def build_graph_neighborhoods(
    conn: sqlite3.Connection,
    *,
    max_distance: int = 3,
    max_centers: int = 1500,
) -> dict[str, Any]:
    """Build undirected N-hop neighborhoods for every graph endpoint."""
    ensure_graphdb_capability_schema(conn)
    node_types = _node_type_map(conn)
    edges = _edge_tuples(conn)
    adjacency: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for e in edges:
        src, tgt, et, eid = (
            str(e.get("source_node_id") or ""),
            str(e.get("target_node_id") or ""),
            str(e.get("edge_type") or ""),
            str(e.get("edge_id") or ""),
        )
        if src and tgt:
            adjacency[src].append((tgt, et, eid))
            adjacency[tgt].append((src, et + "_reverse", eid))
    centers = sorted(adjacency)
    if len(centers) > max_centers:
        raise ValueError(
            "max_centers cannot preserve direct neighborhoods for every endpoint: "
            f"required={len(centers)} configured={max_centers}"
        )
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
    persisted = int(conn.execute("SELECT COUNT(*) FROM graph_neighborhoods").fetchone()[0])
    return {"graph_neighborhoods_materialized": persisted, "max_distance": max_distance}


def materialize_graphdb_capability_indexes(conn: sqlite3.Connection) -> dict[str, Any]:
    """Materialize the versioned direct-only capability used by fresh builds.

    The canonical materializer calls :func:`build_graph_index_rows` before its
    SQLite file exists. Atomic hardening calls this function over the copied
    logical projection. Both therefore use the same direct-edge path,
    neighborhood, and sibling derivation instead of retaining historical
    depth-four/distance-three rows.
    """
    schema = ensure_graphdb_capability_schema(conn)
    node_rows = [
        {"node_id": str(node_id), "node_type": str(node_type)}
        for node_id, node_type in conn.execute("SELECT node_id,node_type FROM graph_nodes ORDER BY node_id")
    ]
    edge_rows = sorted(
        _edge_tuples(conn),
        key=lambda row: (
            str(row.get("source_node_id") or ""),
            str(row.get("target_node_id") or ""),
            str(row.get("edge_type") or ""),
            str(row.get("edge_id") or ""),
        ),
    )
    rows = build_graph_index_rows(
        node_rows=node_rows,
        edge_rows=edge_rows,
        section_rows=(),
        role_family_projection_rows=(),
        created_at=_utc_now(),
    )

    conn.execute("DELETE FROM graph_paths")
    conn.execute("DELETE FROM graph_neighborhoods")
    conn.execute("DELETE FROM graph_sibling_links")
    conn.executemany(
        """
        INSERT INTO graph_paths (
            path_id, start_node_id, end_node_id, path_depth, path_signature,
            node_path_json, edge_path_json, edge_types_json, proof_fact_ids_json,
            metric_ids_json, section_ids_json, path_score, novelty_score,
            proof_strength_score, created_at
        ) VALUES (
            :path_id, :start_node_id, :end_node_id, :path_depth, :path_signature,
            :node_path_json, :edge_path_json, :edge_types_json,
            :proof_fact_ids_json, :metric_ids_json, :section_ids_json,
            :path_score, :novelty_score, :proof_strength_score, :created_at
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
    conn.commit()
    return {
        "schema": schema,
        "graph_index_capability_version": GRAPH_INDEX_CAPABILITY_VERSION,
        "index_mode": "direct_only",
        "paths": {
            "graph_paths_materialized": len(rows["graph_paths"]),
            "max_depth": 1,
        },
        "siblings": {
            "graph_sibling_links_materialized": len(rows["graph_sibling_links"]),
        },
        "neighborhoods": {
            "graph_neighborhoods_materialized": len(rows["graph_neighborhoods"]),
            "max_distance": 1,
        },
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
        (
            run_id,
            resume_section,
            metric_id,
            metric_value,
            fact_id,
            skill_id,
            role_family_key,
            int(usage_count),
            _utc_now(),
        ),
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
    require_graphdb_capability_schema(conn)
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
    require_graphdb_capability_schema(conn)
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


def query_sibling_alternatives(
    conn: sqlite3.Connection, *, node_id: str, limit: int = 25
) -> list[dict[str, Any]]:
    require_graphdb_capability_schema(conn)
    from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
        BLOCKED_SUPPORT_LEVELS,
        NON_PROMOTE_ACTIVATION,
    )

    blocked_activation_placeholders = ",".join("?" for _ in NON_PROMOTE_ACTIVATION)
    blocked_support_placeholders = ",".join("?" for _ in BLOCKED_SUPPORT_LEVELS)
    return [
        {
            "node_id": node_id,
            "sibling_node_id": r[0],
            "sibling_label": r[1],
            "sibling_reason": r[2],
            "shared_parent_node_id": r[3],
            "shared_edge_type": r[4],
            "sibling_score": r[5],
            "shared_context_count": r[6],
        }
        for r in conn.execute(
            f"""
            WITH ranked_siblings AS (
                SELECT
                    s.sibling_node_id,
                    COALESCE(n.label, '') AS sibling_label,
                    s.sibling_reason,
                    s.shared_parent_node_id,
                    s.shared_edge_type,
                    s.sibling_score,
                    COUNT(*) OVER (
                        PARTITION BY s.node_id, s.sibling_node_id
                    ) AS shared_context_count,
                    ROW_NUMBER() OVER (
                        PARTITION BY s.node_id, s.sibling_node_id
                        ORDER BY s.sibling_score DESC,
                                 s.shared_parent_node_id,
                                 s.shared_edge_type,
                                 s.sibling_reason
                    ) AS context_rank
                FROM graph_sibling_links s
                JOIN graph_nodes n ON n.node_id = s.sibling_node_id
                WHERE s.node_id = ?
                  AND n.external_eligible = 1
                  AND COALESCE(n.activation_status, '') NOT IN (
                      {blocked_activation_placeholders}
                  )
                  AND COALESCE(n.support_level, '') NOT IN (
                      {blocked_support_placeholders}
                  )
            )
            SELECT sibling_node_id, sibling_label, sibling_reason,
                   shared_parent_node_id, shared_edge_type, sibling_score,
                   shared_context_count
            FROM ranked_siblings
            WHERE context_rank = 1
            ORDER BY sibling_score DESC, sibling_node_id
            LIMIT ?
            """,
            (
                node_id,
                *sorted(NON_PROMOTE_ACTIVATION),
                *sorted(BLOCKED_SUPPORT_LEVELS),
                limit,
            ),
        )
    ]


def query_section_evidence_budget(
    conn: sqlite3.Connection,
    *,
    section_id: str,
    role_family_key: str = "*",
) -> dict[str, Any] | None:
    require_graphdb_capability_schema(conn)
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
    run_id: str = "",
    limit: int = 25,
) -> list[dict[str, Any]]:
    """Return metric candidates using only the current run's novelty state."""
    require_graphdb_capability_schema(conn)
    budget = query_section_evidence_budget(conn, section_id=section_id, role_family_key=role_family_key) or {}
    forbidden = set(budget.get("forbidden_metric_ids") or [])
    metric_type_placeholders = ",".join("?" for _ in METRIC_NODE_TYPES)
    effective_run_id = str(run_id or "") or "__NO_CURRENT_RUN__"
    rows = conn.execute(
        f"""
        SELECT p.end_node_id, COALESCE(n.label, p.end_node_id), p.start_node_id,
               p.path_signature, p.path_score, p.novelty_score, p.proof_strength_score,
               COALESCE(SUM(u.usage_count), 0) AS prior_usage
        FROM graph_paths p
        LEFT JOIN graph_nodes n ON n.node_id = p.end_node_id
        LEFT JOIN resume_metric_usage u
          ON u.metric_id = p.end_node_id AND u.run_id = ?
        WHERE n.node_type IN ({metric_type_placeholders})
        GROUP BY p.end_node_id, n.label, p.start_node_id, p.path_signature,
                 p.path_score, p.novelty_score, p.proof_strength_score
        ORDER BY prior_usage ASC, p.proof_strength_score DESC, p.novelty_score DESC, p.path_score DESC
        LIMIT ?
        """,
        (effective_run_id, *sorted(METRIC_NODE_TYPES), max(limit * 2, limit)),
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
    "GRAPH_INDEX_CAPABILITY_VERSION",
    "GRAPH_INDEX_SCHEMA_VERSION",
    "METRIC_NODE_TYPES",
    "SIBLING_NODE_TYPES",
    "SKILL_FACT_EVIDENCE_NODE_TYPES",
    "EDGE_METADATA_COLUMNS",
    "build_graph_index_rows",
    "compute_sqlite_graph_digest",
    "compute_sqlite_schema_digest",
    "ensure_graphdb_capability_schema",
    "require_graphdb_capability_schema",
    "validate_graphdb_capability_integrity",
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
