"""Apply SQLite graphDB-like capability indexes for apps_rg C0.3.

This is a zero-loss runtime projection hardener. It never edits the canonical
JSON graph directly and never deletes source graph_nodes/graph_edges rows.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    default_graph_sqlite_path,
    materialize_augmented_skills_graph_sqlite,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    materialize_graphdb_capability_indexes,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def apply_graphdb_capability_sqlite_hardening(
    *,
    repo_root: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or _repo_root()
    path = db_path or default_graph_sqlite_path(root)
    if not path.exists():
        materialize_augmented_skills_graph_sqlite(repo_root=root, db_path=path)
    conn = open_graph_sqlite(repo_root=root, db_path=path, read_only=False)
    try:
        before = {
            name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            for name in ("graph_nodes", "graph_edges", "skill_fact_links")
            if conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            ).fetchone()
        }
        result = materialize_graphdb_capability_indexes(conn)
        after = {
            name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            for name in ("graph_nodes", "graph_edges", "skill_fact_links")
            if conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            ).fetchone()
        }
    finally:
        conn.close()
    decreased = {k: (before[k], after.get(k, 0)) for k in before if after.get(k, 0) < before[k]}
    if decreased:
        raise RuntimeError(f"zero-loss violation: source row counts decreased: {decreased}")
    return {
        "status": "GRAPHDB_CAPABILITY_SQLITE_HARDENED",
        "sqlite_db_path": str(path),
        "before_counts": before,
        "after_counts": after,
        "materialization": result,
    }


def main() -> None:
    print(json.dumps(apply_graphdb_capability_sqlite_hardening(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
