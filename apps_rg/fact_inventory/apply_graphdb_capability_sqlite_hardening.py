"""Apply SQLite graphDB-like capability indexes for apps_rg C0.3.

This is a zero-loss runtime projection hardener. It never edits the canonical
JSON graph directly and never deletes source graph_nodes/graph_edges rows.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    C03_SQLITE_MATERIALIZER_CODE_VERSION,
    DDL_STATEMENTS,
    _acquire_sqlite_maintenance_lock,
    _cleanup_temp_sqlite,
    _new_sibling_temp_db_path,
    _release_sqlite_maintenance_lock,
    _replace_sqlite_projection_if_unchanged,
    _require_sidecar_free_atomic_target,
    _sqlite_projection_digest,
    default_graph_sqlite_path,
    materialize_augmented_skills_graph_sqlite,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    GRAPH_INDEX_SCHEMA_VERSION,
    compute_sqlite_graph_digest,
    materialize_graphdb_capability_indexes,
    validate_graphdb_capability_integrity,
)

_PRESERVED_TABLES = (
    "graph_nodes",
    "graph_edges",
    "skill_fact_links",
    "section_eligibility",
    "role_family_projection",
    "c03_skill_selection_features",
    "c03_role_family_skill_weights",
    "resume_metric_usage",
    "section_evidence_budget",
    "graph_selection_rejections",
)

_MIGRATION_REQUIRED_DEFAULTS: dict[tuple[str, str], Any] = {
    ("graph_nodes", "created_at"): "sqlite_schema_migration",
    ("graph_nodes", "updated_at"): "sqlite_schema_migration",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _table_columns(conn: Any, table_name: str) -> set[str]:
    return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table_name})")}


def _table_exists(conn: Any, table_name: str) -> bool:
    return bool(
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
    )


def _copy_table_into_fresh_schema(source: Any, target: Any, table_name: str) -> None:
    if not _table_exists(source, table_name) or not _table_exists(target, table_name):
        return
    source_columns = _table_columns(source, table_name)
    target_info = target.execute(f"PRAGMA table_info({table_name})").fetchall()
    insert_columns = [str(row[1]) for row in target_info if str(row[1]) in source_columns]
    fallback_columns: list[tuple[str, Any]] = []
    for row in target_info:
        column_name = str(row[1])
        is_not_null = bool(row[3])
        default_sql = row[4]
        is_primary_key = bool(row[5])
        if column_name in insert_columns or default_sql is not None:
            continue
        fallback_key = (table_name, column_name)
        if fallback_key in _MIGRATION_REQUIRED_DEFAULTS:
            fallback_columns.append(
                (column_name, _MIGRATION_REQUIRED_DEFAULTS[fallback_key])
            )
            continue
        if is_not_null or is_primary_key:
            raise ValueError(
                "legacy graph schema cannot be losslessly migrated: "
                f"{table_name}.{column_name} is required"
            )
    if not insert_columns:
        source_count = int(
            source.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        )
        if source_count:
            raise ValueError(
                "legacy graph schema cannot be losslessly migrated: "
                f"{table_name} has no compatible columns"
            )
        return
    select_sql = f"SELECT {','.join(insert_columns)} FROM {table_name}"
    rows = source.execute(select_sql).fetchall()
    all_columns = insert_columns + [name for name, _value in fallback_columns]
    if not all_columns:
        return
    placeholders = ",".join("?" for _ in all_columns)
    values = [
        tuple(row) + tuple(value for _name, value in fallback_columns)
        for row in rows
    ]
    if values:
        target.executemany(
            f"INSERT INTO {table_name} ({','.join(all_columns)}) "
            f"VALUES ({placeholders})",
            values,
        )


def _persist_current_metadata(
    target: Any,
    *,
    source_name: str,
    repo_root: Path,
) -> None:
    sqlite_graph_digest = compute_sqlite_graph_digest(target)
    metadata_rows = target.execute(
        """
        SELECT graph_version, materialized_from, materialized_at, ledger_hash,
               graph_count_summary, authority_status
        FROM graph_metadata
        """
    ).fetchall()
    if len(metadata_rows) > 1:
        raise ValueError(
            f"graphDB capability data invalid: graph_metadata_row_count={len(metadata_rows)}"
        )
    if metadata_rows:
        graph_version, materialized_from, _materialized_at, ledger_hash, raw_summary, _authority = (
            metadata_rows[0]
        )
        if not str(ledger_hash or "").strip():
            raise ValueError("graphDB capability data invalid: graph_metadata ledger_hash is empty")
        try:
            summary = json.loads(raw_summary or "{}")
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(
                "graphDB capability data invalid: graph_metadata summary is invalid JSON"
            ) from exc
        if not isinstance(summary, dict):
            raise ValueError(
                "graphDB capability data invalid: graph_metadata summary is not an object"
            )
        canonical_source = Path(str(materialized_from or ""))
        if not canonical_source.is_absolute():
            canonical_source = repo_root / canonical_source
        if canonical_source.is_file() and canonical_source.suffix.lower() == ".json":
            try:
                canonical_payload = json.loads(
                    canonical_source.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(
                    "graphDB capability data invalid: canonical graph source is unreadable"
                ) from exc
            canonical_digest = hashlib.sha256(
                json.dumps(
                    canonical_payload,
                    sort_keys=True,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            if canonical_digest != ledger_hash:
                raise ValueError(
                    "graphDB capability data invalid: canonical graph source digest mismatch"
                )
            summary.setdefault("canonical_digest_kind", "canonical_payload_v1")
        elif summary.get("canonical_digest_kind") == "canonical_payload_v1":
            raise ValueError(
                "graphDB capability data invalid: canonical graph source is missing"
            )
    else:
        graph_version = "sqlite_projection_migration.v1"
        ledger_hash = sqlite_graph_digest
        summary = {"canonical_digest_kind": "sqlite_projection_logical_v1"}
        target.execute(
            """
            INSERT INTO graph_metadata (
                graph_version, materialized_from, materialized_at, ledger_hash,
                graph_count_summary, authority_status
            ) VALUES (?, ?, ?, ?, '{}', ?)
            """,
            (
                graph_version,
                f"sqlite_projection:{source_name}",
                "sqlite_schema_migration",
                ledger_hash,
                "augmented_skills_graph_authoritative",
            ),
        )
    summary.update(
        {
            "c03_sqlite_materializer_code_version": C03_SQLITE_MATERIALIZER_CODE_VERSION,
            "graph_index_schema_version": GRAPH_INDEX_SCHEMA_VERSION,
            "canonical_graph_digest": str(ledger_hash),
            "sqlite_graph_digest": sqlite_graph_digest,
            "node_count_sqlite": int(target.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0]),
            "edge_count_sqlite": int(target.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0]),
            "skill_fact_link_count": int(target.execute("SELECT COUNT(*) FROM skill_fact_links").fetchone()[0]),
            "graph_path_count": int(target.execute("SELECT COUNT(*) FROM graph_paths").fetchone()[0]),
            "graph_neighborhood_count": int(target.execute("SELECT COUNT(*) FROM graph_neighborhoods").fetchone()[0]),
            "graph_sibling_link_count": int(target.execute("SELECT COUNT(*) FROM graph_sibling_links").fetchone()[0]),
            "section_evidence_budget_count": int(target.execute("SELECT COUNT(*) FROM section_evidence_budget").fetchone()[0]),
        }
    )
    target.execute(
        "UPDATE graph_metadata SET graph_count_summary=? WHERE graph_version=?",
        (json.dumps(summary, sort_keys=True, separators=(",", ":")), graph_version),
    )


def apply_graphdb_capability_sqlite_hardening(
    *,
    repo_root: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or _repo_root()
    path = db_path or default_graph_sqlite_path(root)
    if not path.exists():
        materialize_augmented_skills_graph_sqlite(repo_root=root, db_path=path)
    maintenance_lock = _acquire_sqlite_maintenance_lock(path)
    expected_target_digest = _sqlite_projection_digest(path)
    try:
        _require_sidecar_free_atomic_target(path)
        temp_path = _new_sibling_temp_db_path(path)
    except (OSError, RuntimeError):
        _release_sqlite_maintenance_lock(maintenance_lock)
        raise
    source = None
    conn = None
    hardening_succeeded = False
    try:
        source = open_graph_sqlite(repo_root=root, db_path=path, read_only=True)
        conn = open_graph_sqlite(repo_root=root, db_path=temp_path, read_only=False)
        before = {
            name: source.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            for name in ("graph_nodes", "graph_edges", "skill_fact_links")
            if source.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            ).fetchone()
        }
        broken_graph_edges = int(
            source.execute(
                """
                SELECT COUNT(*) FROM graph_edges e
                LEFT JOIN graph_nodes s ON s.node_id = e.source_node_id
                LEFT JOIN graph_nodes t ON t.node_id = e.target_node_id
                WHERE s.node_id IS NULL OR t.node_id IS NULL
                """
            ).fetchone()[0]
        )
        if broken_graph_edges:
            raise ValueError(
                "graphDB capability data invalid: "
                f"broken_graph_edges={broken_graph_edges}"
            )
        for ddl in DDL_STATEMENTS:
            conn.execute(ddl)
        for table_name in _PRESERVED_TABLES:
            _copy_table_into_fresh_schema(source, conn, table_name)
        if _table_exists(source, "graph_metadata"):
            source_metadata_columns = _table_columns(source, "graph_metadata")
            required_metadata_columns = {
                "graph_version",
                "materialized_from",
                "materialized_at",
                "ledger_hash",
                "graph_count_summary",
                "authority_status",
            }
            if required_metadata_columns.issubset(source_metadata_columns):
                _copy_table_into_fresh_schema(source, conn, "graph_metadata")
        conn.commit()
        result = materialize_graphdb_capability_indexes(conn)
        _persist_current_metadata(
            conn,
            source_name=path.name,
            repo_root=root,
        )
        conn.commit()
        integrity = validate_graphdb_capability_integrity(
            conn,
            expected_materializer_version=C03_SQLITE_MATERIALIZER_CODE_VERSION,
        )
        after = {
            name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            for name in ("graph_nodes", "graph_edges", "skill_fact_links")
            if conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            ).fetchone()
        }
        if before != after:
            raise RuntimeError(
                f"zero-loss violation: source row counts changed: before={before}, after={after}"
            )
        hardening_succeeded = True
    finally:
        if source is not None:
            source.close()
        if conn is not None:
            conn.close()
        if not hardening_succeeded:
            _cleanup_temp_sqlite(temp_path)
            _release_sqlite_maintenance_lock(maintenance_lock)

    try:
        _replace_sqlite_projection_if_unchanged(
            target=path,
            replacement=temp_path,
            expected_digest=expected_target_digest,
        )
    except (OSError, RuntimeError):
        _cleanup_temp_sqlite(temp_path)
        raise
    finally:
        _release_sqlite_maintenance_lock(maintenance_lock)
    return {
        "status": "GRAPHDB_CAPABILITY_SQLITE_HARDENED",
        "sqlite_db_path": str(path),
        "before_counts": before,
        "after_counts": after,
        "materialization": result,
        "integrity": integrity,
        "atomic_replace": True,
    }


def main() -> None:
    print(json.dumps(apply_graphdb_capability_sqlite_hardening(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
