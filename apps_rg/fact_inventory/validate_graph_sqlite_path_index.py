"""Validate apps_rg SQLite graphDB-like capability hardening."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    C03_SQLITE_MATERIALIZER_CODE_VERSION,
    default_graph_sqlite_path,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    GRAPH_INDEX_SCHEMA_VERSION,
    compute_sqlite_graph_digest,
    require_graphdb_capability_schema,
    table_columns,
    table_exists,
    validate_graphdb_capability_integrity,
)

if TYPE_CHECKING:
    from agentic_core.L4_state.adapters import sqlite3_adapter as sqlite3

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
    materialize_if_missing: bool = False,
) -> dict[str, Any]:
    if materialize_if_missing:
        raise ValueError(
            "validation is strictly read-only; use the explicit applicator "
            "apply_graphdb_capability_sqlite_hardening instead"
        )
    root = repo_root or _repo_root()
    path = db_path or default_graph_sqlite_path(root)
    if not path.exists():
        raise FileNotFoundError(f"SQLite graph projection not found: {path}")
    conn = open_graph_sqlite(repo_root=root, db_path=path, read_only=True)
    errors: list[str] = []
    try:
        before = {
            "graph_nodes": _count(conn, "graph_nodes"),
            "graph_edges": _count(conn, "graph_edges"),
            "skill_fact_links": _count(conn, "skill_fact_links"),
        }
        schema = require_graphdb_capability_schema(conn)
        integrity = validate_graphdb_capability_integrity(
            conn,
            expected_materializer_version=C03_SQLITE_MATERIALIZER_CODE_VERSION,
        )
        after = {
            "graph_nodes": _count(conn, "graph_nodes"),
            "graph_edges": _count(conn, "graph_edges"),
            "skill_fact_links": _count(conn, "skill_fact_links"),
        }
        for table in REQUIRED_TABLES:
            if not table_exists(conn, table):
                errors.append(f"missing table: {table}")
        if not table_exists(conn, "graph_edges_reverse"):
            errors.append("missing view: graph_edges_reverse")
        if after != before:
            errors.append(f"read purity violation: source counts changed {before}->{after}")
        if _count(conn, "graph_paths") == 0 and _count(conn, "graph_edges") > 0:
            errors.append("graph_paths empty despite graph_edges being present")
        if _count(conn, "section_evidence_budget") < 5:
            errors.append("section_evidence_budget missing conservative defaults")
        metadata_summary: dict[str, Any] | None = None
        meta_cols = table_columns(conn, "graph_metadata") if table_exists(conn, "graph_metadata") else set()
        if "ledger_hash" not in meta_cols:
            errors.append("graph_metadata with ledger_hash is required")
        else:
            metadata_rows = conn.execute(
                "SELECT materialized_from, ledger_hash, graph_count_summary FROM graph_metadata"
            ).fetchall()
            if len(metadata_rows) != 1:
                errors.append(
                    f"graph_metadata row count must be exactly one: {len(metadata_rows)}"
                )
            row = metadata_rows[0] if metadata_rows else None
            if not row or not str(row[1] or "").strip():
                errors.append("graph_metadata.ledger_hash is empty")
            if row:
                try:
                    summary = json.loads(row[2] or "{}")
                except (TypeError, json.JSONDecodeError):
                    errors.append("graph_metadata.graph_count_summary is invalid JSON")
                else:
                    if not isinstance(summary, dict):
                        errors.append("graph_metadata.graph_count_summary is not an object")
                    else:
                        metadata_summary = summary
                        if summary.get("graph_index_schema_version") != GRAPH_INDEX_SCHEMA_VERSION:
                            errors.append(
                                "graph_metadata graph_index_schema_version mismatch: "
                                f"{summary.get('graph_index_schema_version')!r}"
                            )
                        if (
                            summary.get("c03_sqlite_materializer_code_version")
                            != C03_SQLITE_MATERIALIZER_CODE_VERSION
                        ):
                            errors.append(
                                "graph_metadata materializer version mismatch: "
                                f"{summary.get('c03_sqlite_materializer_code_version')!r}"
                            )
                        if summary.get("canonical_graph_digest") != row[1]:
                            errors.append("graph_metadata canonical digest does not match ledger_hash")
                        if summary.get("sqlite_graph_digest") != compute_sqlite_graph_digest(conn):
                            errors.append("graph_metadata SQLite graph digest mismatch")
                        materialized_from = str(row[0] or "").strip()
                        source_path = Path(materialized_from)
                        if not source_path.is_absolute():
                            source_path = root / source_path
                        digest_kind = summary.get("canonical_digest_kind")
                        if source_path.is_file() and source_path.suffix.lower() == ".json":
                            try:
                                source_payload = json.loads(source_path.read_text(encoding="utf-8"))
                            except (OSError, json.JSONDecodeError) as exc:
                                errors.append(f"canonical graph source unreadable: {exc}")
                            else:
                                canonical_digest = hashlib.sha256(
                                    json.dumps(
                                        source_payload,
                                        sort_keys=True,
                                        ensure_ascii=False,
                                        separators=(",", ":"),
                                    ).encode("utf-8")
                                ).hexdigest()
                                if canonical_digest != row[1]:
                                    errors.append("canonical graph source digest mismatch")
                        elif digest_kind == "canonical_payload_v1":
                            errors.append(
                                f"canonical graph source is missing: {source_path}"
                            )
                        elif digest_kind != "sqlite_projection_logical_v1":
                            errors.append(
                                f"unsupported canonical digest kind: {digest_kind!r}"
                            )
        if errors:
            raise ValueError("; ".join(errors))
        return {
            "status": "PASS",
            "sqlite_db_path": str(path),
            "counts_before": before,
            "counts_after": after,
            "schema": schema,
            "integrity": integrity,
            "graph_paths": _count(conn, "graph_paths"),
            "graph_sibling_links": _count(conn, "graph_sibling_links"),
            "graph_neighborhoods": _count(conn, "graph_neighborhoods"),
            "section_evidence_budget": _count(conn, "section_evidence_budget"),
            "metadata": metadata_summary,
        }
    finally:
        conn.close()


def main() -> None:
    print(json.dumps(validate_graph_sqlite_path_index(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
