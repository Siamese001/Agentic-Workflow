"""Validate apps_rg SQLite graphDB-like capability hardening."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentic_core.L4_state.adapters import sqlite3_adapter as sqlite3

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    default_graph_sqlite_path,
    materialize_augmented_skills_graph_sqlite,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    EDGE_METADATA_COLUMNS,
    ensure_graphdb_capability_schema,
    materialize_graphdb_capability_indexes,
    table_columns,
    table_exists,
)


REQUIRED_TABLES = (
    "graph_paths",
    "graph_sibling_links",
    "graph_neighborhoods",
    "resume_metric_usage",
    "section_evidence_budget",
    "graph_selection_rejections",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _count(conn: sqlite3.Connection, table: str) -> int:
    if not table_exists(conn, table):
        return 0
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def validate_graph_sqlite_path_index(
    *,
    repo_root: Path | None = None,
    db_path: Path | None = None,
    materialize_if_missing: bool = True,
) -> dict[str, Any]:
    root = repo_root or _repo_root()
    path = db_path or default_graph_sqlite_path(root)
    if materialize_if_missing and not path.exists():
        materialize_augmented_skills_graph_sqlite(repo_root=root, db_path=path)
    if not path.exists():
        raise FileNotFoundError(f"SQLite graph projection not found: {path}")
    conn = open_graph_sqlite(repo_root=root, db_path=path, read_only=False)
    errors: list[str] = []
    try:
        before = {"graph_nodes": _count(conn, "graph_nodes"), "graph_edges": _count(conn, "graph_edges"), "skill_fact_links": _count(conn, "skill_fact_links")}
        ensure_graphdb_capability_schema(conn)
        materialize_graphdb_capability_indexes(conn)
        after = {"graph_nodes": _count(conn, "graph_nodes"), "graph_edges": _count(conn, "graph_edges"), "skill_fact_links": _count(conn, "skill_fact_links")}
        for table in REQUIRED_TABLES:
            if not table_exists(conn, table):
                errors.append(f"missing table: {table}")
        if not table_exists(conn, "graph_edges_reverse"):
            errors.append("missing view: graph_edges_reverse")
        edge_cols = table_columns(conn, "graph_edges")
        for col, _ddl in EDGE_METADATA_COLUMNS:
            if col not in edge_cols:
                errors.append(f"graph_edges missing column: {col}")
        for key, value in before.items():
            if after.get(key, 0) < value:
                errors.append(f"zero-loss violation: {key} decreased {value}->{after.get(key, 0)}")
        if _count(conn, "graph_paths") == 0 and _count(conn, "graph_edges") > 0:
            errors.append("graph_paths empty despite graph_edges being present")
        if _count(conn, "section_evidence_budget") < 5:
            errors.append("section_evidence_budget missing conservative defaults")
        meta_cols = table_columns(conn, "graph_metadata") if table_exists(conn, "graph_metadata") else set()
        if "ledger_hash" in meta_cols:
            row = conn.execute("SELECT ledger_hash FROM graph_metadata LIMIT 1").fetchone()
            if not row or not str(row[0] or "").strip():
                errors.append("graph_metadata.ledger_hash is empty")
        if errors:
            raise ValueError("; ".join(errors))
        return {
            "status": "PASS",
            "sqlite_db_path": str(path),
            "counts_before": before,
            "counts_after": after,
            "graph_paths": _count(conn, "graph_paths"),
            "graph_sibling_links": _count(conn, "graph_sibling_links"),
            "graph_neighborhoods": _count(conn, "graph_neighborhoods"),
            "section_evidence_budget": _count(conn, "section_evidence_budget"),
        }
    finally:
        conn.close()


def main() -> None:
    print(json.dumps(validate_graph_sqlite_path_index(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
