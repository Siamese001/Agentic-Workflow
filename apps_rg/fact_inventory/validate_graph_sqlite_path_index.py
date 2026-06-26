"""Validate the generated apps_rg SQLite graph-index projection.

The canonical graph remains JSON. This validator materializes a temporary
SQLite projection by default and checks that graph-engine helper tables/views
exist without reducing core graph counts.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    build_skill_rows_by_id,
    materialize_augmented_skills_graph_sqlite,
    open_graph_sqlite,
    validate_materialized_sqlite,
)

REQUIRED_EDGE_COLUMNS = {
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
}

REQUIRED_OBJECTS = {
    ("view", "graph_edges_reverse"),
    ("table", "graph_paths"),
    ("table", "graph_sibling_links"),
    ("table", "graph_neighborhoods"),
    ("table", "resume_metric_usage"),
    ("table", "section_evidence_budget"),
    ("table", "graph_selection_rejections"),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _object_set(conn: sqlite3.Connection) -> set[tuple[str, str]]:
    return {
        (str(row["type"]), str(row["name"]))
        for row in conn.execute(
            "SELECT type, name FROM sqlite_master WHERE type IN ('table', 'view')"
        ).fetchall()
    }


def _edge_columns(conn: sqlite3.Connection) -> set[str]:
    return {str(row["name"]) for row in conn.execute("PRAGMA table_info(graph_edges)").fetchall()}


def validate_graph_sqlite_path_index(
    *,
    repo_root: Path | None = None,
    db_path: Path | None = None,
    materialize: bool = True,
) -> dict[str, Any]:
    """Validate graph-index tables/views and core count invariants."""
    root = repo_root or _repo_root()
    graph = load_augmented_skills_graph(repo_root=root)
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    path = db_path
    if path is None:
        temp_dir = tempfile.TemporaryDirectory()
        path = Path(temp_dir.name) / "augmented_skills_graph.sqlite"
    try:
        if materialize:
            materialize_augmented_skills_graph_sqlite(repo_root=root, db_path=path)
        if not path.is_file():
            return {"status": "FAIL", "issues": ["sqlite_missing"], "sqlite_db_path": str(path)}

        try:
            base = validate_materialized_sqlite(graph=graph, repo_root=root, db_path=path)
        except (sqlite3.Error, ValueError, OSError) as exc:
            return {
                "status": "FAIL",
                "issues": [f"sqlite_validation_error:{type(exc).__name__}:{exc}"],
                "sqlite_db_path": str(path),
                "canonical_graph": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
                "sqlite_projection_canonical": False,
            }
        issues = list(base.get("issues") or [])
        conn = _connect(path)
        try:
            objects = _object_set(conn)
            missing_objects = sorted(REQUIRED_OBJECTS - objects)
            missing_edge_columns = sorted(REQUIRED_EDGE_COLUMNS - _edge_columns(conn))
            counts = {
                "graph_node_count": conn.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0],
                "graph_edge_count": conn.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0],
                "skill_fact_link_count": conn.execute("SELECT COUNT(*) FROM skill_fact_links").fetchone()[0],
                "skill_node_count": conn.execute(
                    "SELECT COUNT(*) FROM graph_nodes WHERE node_type='skill'"
                ).fetchone()[0],
                "graph_path_count": conn.execute("SELECT COUNT(*) FROM graph_paths").fetchone()[0]
                if ("table", "graph_paths") in objects
                else 0,
                "graph_sibling_link_count": conn.execute(
                    "SELECT COUNT(*) FROM graph_sibling_links"
                ).fetchone()[0]
                if ("table", "graph_sibling_links") in objects
                else 0,
                "graph_neighborhood_count": conn.execute(
                    "SELECT COUNT(*) FROM graph_neighborhoods"
                ).fetchone()[0]
                if ("table", "graph_neighborhoods") in objects
                else 0,
                "section_evidence_budget_count": conn.execute(
                    "SELECT COUNT(*) FROM section_evidence_budget"
                ).fetchone()[0]
                if ("table", "section_evidence_budget") in objects
                else 0,
                "metric_outcome_count": conn.execute(
                    "SELECT COUNT(*) FROM graph_nodes WHERE node_type='metric_outcome'"
                ).fetchone()[0],
                "metadata_hash_count": conn.execute(
                    "SELECT COUNT(*) FROM graph_metadata WHERE COALESCE(ledger_hash, '') <> ''"
                ).fetchone()[0],
            }
            broad_ref = conn.execute(
                """
                SELECT COUNT(*) FROM graph_nodes
                WHERE source_authority LIKE '%broad_skills_ledger%'
                """
            ).fetchone()[0]
        finally:
            conn.close()

        expected_skill_rows = len(build_skill_rows_by_id(graph))
        if missing_objects:
            issues.append(f"missing_objects:{missing_objects}")
        if missing_edge_columns:
            issues.append(f"missing_graph_edges_columns:{missing_edge_columns}")
        if counts["graph_node_count"] < int(graph.get("graph_metadata", {}).get("node_count") or 0):
            issues.append("graph_node_count_decreased")
        if counts["graph_edge_count"] < len(
            [e for e in graph.get("graph_edges") or [] if isinstance(e, dict) and e.get("edge_id")]
        ):
            issues.append("graph_edge_count_decreased")
        if counts["skill_fact_link_count"] <= 0:
            issues.append("skill_fact_links_empty")
        if counts["skill_node_count"] < expected_skill_rows:
            issues.append("skill_node_count_decreased")
        if counts["graph_path_count"] <= 0:
            issues.append("graph_paths_empty")
        if counts["graph_sibling_link_count"] <= 0:
            issues.append("graph_sibling_links_empty")
        if counts["graph_neighborhood_count"] <= 0:
            issues.append("graph_neighborhoods_empty")
        if counts["section_evidence_budget_count"] <= 0:
            issues.append("section_evidence_budget_empty")
        if counts["metadata_hash_count"] <= 0:
            issues.append("graph_metadata_ledger_hash_missing")
        if broad_ref:
            issues.append(f"broad_skills_ledger_authority_introduced:{broad_ref}")
        if counts["metric_outcome_count"] > 0 and base.get("status") != "PASS":
            issues.append("metric_outcome_nodes_not_cleanly_queryable")

        return {
            "status": "PASS" if not issues else "FAIL",
            "issues": issues,
            "sqlite_db_path": str(path),
            "base_status": base.get("status"),
            "counts": counts,
            "missing_objects": missing_objects,
            "missing_graph_edges_columns": missing_edge_columns,
            "canonical_graph": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            "sqlite_projection_canonical": False,
        }
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", type=Path, default=None)
    parser.add_argument("--no-materialize", action="store_true")
    args = parser.parse_args(argv)
    result = validate_graph_sqlite_path_index(
        repo_root=_repo_root(),
        db_path=args.db_path,
        materialize=not args.no_materialize,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
