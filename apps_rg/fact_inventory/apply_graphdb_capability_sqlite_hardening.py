"""Apply SQLite graphDB-like capability indexes for apps_rg C0.3.

This is a zero-loss runtime projection hardener. It never edits the canonical
JSON graph directly and never deletes source graph_nodes/graph_edges rows.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    C03_SQLITE_MATERIALIZER_CODE_VERSION,
    DDL_STATEMENTS,
    _acquire_sqlite_maintenance_lock,
    _cleanup_temp_sqlite,
    _new_sibling_temp_db_path,
    _open_isolated_temp_graph_sqlite,
    _release_sqlite_maintenance_lock,
    _replace_sqlite_projection_if_unchanged,
    _require_sidecar_free_atomic_target,
    _sqlite_projection_digest,
    default_graph_sqlite_path,
    materialize_augmented_skills_graph_sqlite,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    GRAPH_INDEX_CAPABILITY_VERSION,
    GRAPH_INDEX_SCHEMA_VERSION,
    compute_sqlite_graph_digest,
    compute_sqlite_schema_digest,
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

_OPTIONAL_PRESERVED_TABLES = ("graph_metadata",)

_IMMUTABLE_AUTHORITY_TABLES = (
    "graph_nodes",
    "graph_edges",
    "skill_fact_links",
    "section_eligibility",
    "role_family_projection",
    "c03_skill_selection_features",
    "c03_role_family_skill_weights",
    "section_evidence_budget",
)

_VOLATILE_AUTHORITY_COLUMNS = frozenset({"created_at", "updated_at"})
_LEGACY_AUTHORITY_TABLES = frozenset({"graph_nodes", "graph_edges", "skill_fact_links"})

_MIGRATION_REQUIRED_DEFAULTS: dict[tuple[str, str], Any] = {
    ("graph_nodes", "created_at"): "sqlite_schema_migration",
    ("graph_nodes", "updated_at"): "sqlite_schema_migration",
}


class UnsupportedGraphSchemaError(ValueError):
    """Fail-closed diagnostic for source schema that cannot be preserved."""

    def __init__(
        self,
        *,
        unsupported_objects: tuple[str, ...] = (),
        unsupported_columns: tuple[str, ...] = (),
    ) -> None:
        self.unsupported_objects = tuple(sorted(unsupported_objects))
        self.unsupported_columns = tuple(sorted(unsupported_columns))
        diagnostics: list[str] = []
        if self.unsupported_objects:
            diagnostics.append("unsupported_objects=" + ",".join(self.unsupported_objects))
        if self.unsupported_columns:
            diagnostics.append("unsupported_columns=" + ",".join(self.unsupported_columns))
        detail = "; ".join(diagnostics) or "unsupported schema extension"
        super().__init__(
            "graphDB capability schema cannot be losslessly hardened: "
            f"{detail}; migrate or remove these schema extensions explicitly"
        )


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


def _normalize_schema_sql(value: Any) -> str:
    return " ".join(str(value or "").split()).casefold()


_SUPPORTED_LEGACY_TABLE_SQL: dict[str, frozenset[str]] = {
    "graph_nodes": frozenset(
        {
            _normalize_schema_sql(
                """
                CREATE TABLE graph_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    activation_status TEXT NOT NULL DEFAULT 'ACTIVE_CONFIRMED',
                    support_level TEXT NOT NULL DEFAULT 'DIRECT_FROM_RESUME_ARCHIVE'
                )
                """
            )
        }
    ),
    "graph_edges": frozenset(
        {
            _normalize_schema_sql(
                """
                CREATE TABLE graph_edges (
                    edge_id TEXT PRIMARY KEY,
                    source_node_id TEXT NOT NULL,
                    target_node_id TEXT NOT NULL,
                    edge_type TEXT NOT NULL
                )
                """
            )
        }
    ),
    "skill_fact_links": frozenset(
        {
            _normalize_schema_sql(
                """
                CREATE TABLE skill_fact_links (
                    skill_id TEXT NOT NULL,
                    fact_id TEXT NOT NULL,
                    PRIMARY KEY (skill_id, fact_id)
                )
                """
            )
        }
    ),
}


def _user_schema_inventory(conn: Any) -> dict[str, tuple[str, str]]:
    """Return user-defined schema objects, excluding SQLite-owned internals."""
    return {
        str(name): (str(object_type), _normalize_schema_sql(sql))
        for object_type, name, sql in conn.execute(
            """
            SELECT type,name,sql
            FROM sqlite_master
            WHERE type IN ('table','view','index','trigger')
              AND name NOT GLOB 'sqlite_*'
            ORDER BY type,name
            """
        )
    }


def _validate_supported_source_schema(source: Any, target: Any) -> None:
    source_objects = _user_schema_inventory(source)
    target_objects = _user_schema_inventory(target)
    unsupported_objects = [
        f"{object_type}:{name}"
        for name, (object_type, source_sql) in source_objects.items()
        if (
            name not in target_objects
            or target_objects[name][0] != object_type
            or (object_type != "table" and target_objects[name][1] != source_sql)
        )
    ]
    unsupported_columns: list[str] = []
    for name, (object_type, source_sql) in source_objects.items():
        if object_type != "table" or name not in target_objects or target_objects[name][0] != "table":
            continue
        source_columns = _table_columns(source, name)
        target_columns = _table_columns(target, name)
        extra_columns = source_columns - target_columns
        for column_name in sorted(extra_columns):
            unsupported_columns.append(f"{name}.{column_name}")
        if extra_columns:
            continue
        target_sql = target_objects[name][1]
        if source_columns == target_columns:
            if source_sql != target_sql:
                unsupported_objects.append(f"table:{name}")
            continue
        if source_sql not in _SUPPORTED_LEGACY_TABLE_SQL.get(name, frozenset()):
            unsupported_objects.append(f"table:{name}")
    if unsupported_objects or unsupported_columns:
        raise UnsupportedGraphSchemaError(
            unsupported_objects=tuple(unsupported_objects),
            unsupported_columns=tuple(unsupported_columns),
        )


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _canonical_sqlite_value(value: Any) -> tuple[str, str | None]:
    if value is None:
        return ("null", None)
    if isinstance(value, bytes):
        return ("blob", value.hex())
    if isinstance(value, int):
        return ("integer", str(value))
    if isinstance(value, float):
        return ("real", value.hex())
    return ("text", str(value))


def _canonical_table_rows(
    conn: Any,
    *,
    table_name: str,
    columns: tuple[str, ...],
) -> tuple[str, ...]:
    quoted_table = _quote_identifier(table_name)
    quoted_columns = ",".join(_quote_identifier(column) for column in columns)
    rows = conn.execute(f"SELECT {quoted_columns} FROM {quoted_table}").fetchall()
    return tuple(
        sorted(
            json.dumps(
                [_canonical_sqlite_value(value) for value in row],
                ensure_ascii=False,
                separators=(",", ":"),
            )
            for row in rows
        )
    )


def _table_content_digest(
    conn: Any,
    *,
    table_name: str,
    columns: tuple[str, ...],
) -> str:
    canonical_rows = _canonical_table_rows(
        conn,
        table_name=table_name,
        columns=columns,
    )
    digest = hashlib.sha256()
    for row in canonical_rows:
        digest.update(row.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _source_preservation_profile(source: Any) -> dict[str, dict[str, Any]]:
    profile: dict[str, dict[str, Any]] = {}
    for table_name in (*_PRESERVED_TABLES, *_OPTIONAL_PRESERVED_TABLES):
        if not _table_exists(source, table_name):
            continue
        columns = tuple(sorted(_table_columns(source, table_name)))
        profile[table_name] = {
            "columns": columns,
            "count": int(
                source.execute(f"SELECT COUNT(*) FROM {_quote_identifier(table_name)}").fetchone()[0]
            ),
            "digest": _table_content_digest(
                source,
                table_name=table_name,
                columns=columns,
            ),
            "rows": _canonical_table_rows(
                source,
                table_name=table_name,
                columns=columns,
            ),
        }
    return profile


def _verify_preserved_copy(
    target: Any,
    profile: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    copied_counts: dict[str, int] = {}
    copied_digests: dict[str, str] = {}
    for table_name, expected in profile.items():
        copied_counts[table_name] = int(
            target.execute(f"SELECT COUNT(*) FROM {_quote_identifier(table_name)}").fetchone()[0]
        )
        copied_digests[table_name] = _table_content_digest(
            target,
            table_name=table_name,
            columns=expected["columns"],
        )
    source_counts = {table_name: int(expected["count"]) for table_name, expected in profile.items()}
    source_digests = {table_name: str(expected["digest"]) for table_name, expected in profile.items()}
    if source_counts != copied_counts or source_digests != copied_digests:
        raise RuntimeError(
            "zero-loss violation: preserved table copy mismatch: "
            f"source_counts={source_counts}, copied_counts={copied_counts}, "
            f"source_digests={source_digests}, copied_digests={copied_digests}"
        )
    return {
        "status": "PRESERVED_TABLES_VERIFIED",
        "verified_tables": sorted(profile),
        "source_counts": source_counts,
        "copied_counts": copied_counts,
        "source_digests": source_digests,
        "copied_digests": copied_digests,
    }


def _verify_preserved_rows_remain(
    target: Any,
    profile: dict[str, dict[str, Any]],
) -> dict[str, int]:
    final_counts: dict[str, int] = {}
    missing_rows: dict[str, int] = {}
    for table_name in _PRESERVED_TABLES:
        if table_name not in profile:
            continue
        expected = profile[table_name]
        final_rows = Counter(
            _canonical_table_rows(
                target,
                table_name=table_name,
                columns=expected["columns"],
            )
        )
        missing = Counter(expected["rows"]) - final_rows
        if missing:
            missing_rows[table_name] = sum(missing.values())
        final_counts[table_name] = int(
            target.execute(f"SELECT COUNT(*) FROM {_quote_identifier(table_name)}").fetchone()[0]
        )
    if missing_rows:
        raise RuntimeError(
            f"zero-loss violation: source rows missing after materialization: missing_rows={missing_rows}"
        )
    return final_counts


def _canonical_payload_digest(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _immutable_authority_profile(
    conn: Any,
    *,
    columns_from: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, dict[str, Any]]:
    profile: dict[str, dict[str, Any]] = {}
    for table_name in _IMMUTABLE_AUTHORITY_TABLES:
        if not _table_exists(conn, table_name):
            raise ValueError(
                "graphDB capability source authority unavailable: "
                f"required immutable table missing: {table_name}"
            )
        available = _table_columns(conn, table_name)
        if columns_from is None:
            columns = tuple(sorted(available - _VOLATILE_AUTHORITY_COLUMNS))
        else:
            columns = columns_from[table_name]
            missing = set(columns) - available
            if missing:
                raise ValueError(
                    "graphDB capability canonical rebuild missing authority columns: "
                    f"{table_name}.{sorted(missing)!r}"
                )
        profile[table_name] = {
            "columns": columns,
            "count": int(conn.execute(f"SELECT COUNT(*) FROM {_quote_identifier(table_name)}").fetchone()[0]),
            "digest": _table_content_digest(
                conn,
                table_name=table_name,
                columns=columns,
            ),
        }
    return profile


def _source_metadata_row(source: Any) -> tuple[Any, ...] | None:
    if not _table_exists(source, "graph_metadata"):
        return None
    rows = source.execute(
        """
        SELECT graph_version, materialized_from, ledger_hash, graph_count_summary
        FROM graph_metadata
        """
    ).fetchall()
    if len(rows) > 1:
        raise ValueError(f"graphDB capability source authority invalid: graph_metadata_row_count={len(rows)}")
    return tuple(rows[0]) if rows else None


def _validate_source_projection_authority(
    source: Any,
    *,
    repo_root: Path,
    source_path: Path,
) -> dict[str, Any]:
    metadata = _source_metadata_row(source)
    if metadata is None:
        source_tables = {
            name
            for name, (object_type, _sql) in _user_schema_inventory(source).items()
            if object_type == "table"
        }
        if source_tables == _LEGACY_AUTHORITY_TABLES:
            return {
                "status": "LEGACY_SCHEMA_AUTHORITY_WHITELISTED",
                "authority_kind": "exact_legacy_schema",
            }
        raise ValueError("graphDB capability source authority unavailable: trusted metadata is missing")

    _graph_version, materialized_from, ledger_hash, raw_summary = metadata
    try:
        summary = json.loads(raw_summary or "{}")
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "graphDB capability source authority invalid: metadata summary is invalid JSON"
        ) from exc
    if not isinstance(summary, dict):
        raise ValueError("graphDB capability source authority invalid: metadata summary is not an object")

    canonical_source = Path(str(materialized_from or ""))
    if not canonical_source.is_absolute():
        canonical_source = repo_root / canonical_source
    if canonical_source.is_file() and canonical_source.suffix.lower() == ".json":
        try:
            canonical_payload = json.loads(canonical_source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                "graphDB capability source authority invalid: canonical source is unreadable"
            ) from exc
        if not isinstance(canonical_payload, dict):
            raise ValueError("graphDB capability source authority invalid: canonical source is not an object")
        if _canonical_payload_digest(canonical_payload) != str(ledger_hash or ""):
            raise ValueError("graphDB capability source authority invalid: canonical source digest mismatch")

        authority_path = _new_sibling_temp_db_path(source_path)
        authority_conn = None
        try:
            materialize_augmented_skills_graph_sqlite(
                graph=canonical_payload,
                repo_root=repo_root,
                db_path=authority_path,
                json_source_path=canonical_source,
            )
            authority_conn = open_graph_sqlite(
                repo_root=repo_root,
                db_path=authority_path,
                read_only=True,
            )
            authority_conn.execute("BEGIN")
            source_profile = _immutable_authority_profile(source)
            authority_profile = _immutable_authority_profile(
                authority_conn,
                columns_from={
                    table_name: tuple(row["columns"]) for table_name, row in source_profile.items()
                },
            )
            if source_profile != authority_profile:
                mismatched = sorted(
                    table_name
                    for table_name in source_profile
                    if source_profile[table_name] != authority_profile[table_name]
                )
                raise ValueError(
                    "graphDB capability source authority mismatch against canonical rebuild: "
                    f"tables={mismatched}"
                )
        finally:
            if authority_conn is not None:
                authority_conn.close()
            _cleanup_temp_sqlite(authority_path)
        return {
            "status": "CANONICAL_REBUILD_AUTHORITY_VERIFIED",
            "authority_kind": "fresh_canonical_immutable_projection",
            "verified_tables": list(_IMMUTABLE_AUTHORITY_TABLES),
        }

    stored_digest = str(summary.get("sqlite_graph_digest") or "")
    if len(stored_digest) != 64:
        raise ValueError(
            "graphDB capability source authority unavailable: no canonical rebuild or trusted logical digest"
        )
    observed_digest = compute_sqlite_graph_digest(source)
    if stored_digest != observed_digest:
        raise ValueError(
            "graphDB capability source authority mismatch: stored logical digest does not match source"
        )
    return {
        "status": "STORED_LOGICAL_DIGEST_AUTHORITY_VERIFIED",
        "authority_kind": "stored_sqlite_graph_digest",
        "sqlite_graph_digest": observed_digest,
    }


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
            fallback_columns.append((column_name, _MIGRATION_REQUIRED_DEFAULTS[fallback_key]))
            continue
        if is_not_null or is_primary_key:
            raise ValueError(
                f"legacy graph schema cannot be losslessly migrated: {table_name}.{column_name} is required"
            )
    if not insert_columns:
        source_count = int(source.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])
        if source_count:
            raise ValueError(
                f"legacy graph schema cannot be losslessly migrated: {table_name} has no compatible columns"
            )
        return
    select_sql = f"SELECT {','.join(insert_columns)} FROM {table_name}"
    rows = source.execute(select_sql).fetchall()
    all_columns = insert_columns + [name for name, _value in fallback_columns]
    if not all_columns:
        return
    placeholders = ",".join("?" for _ in all_columns)
    values = [tuple(row) + tuple(value for _name, value in fallback_columns) for row in rows]
    if values:
        target.executemany(
            f"INSERT INTO {table_name} ({','.join(all_columns)}) VALUES ({placeholders})",
            values,
        )


def _persist_current_metadata(
    target: Any,
    *,
    source_name: str,
    repo_root: Path,
) -> None:
    sqlite_graph_digest = compute_sqlite_graph_digest(target)
    sqlite_schema_digest = compute_sqlite_schema_digest(target)
    metadata_rows = target.execute(
        """
        SELECT graph_version, materialized_from, materialized_at, ledger_hash,
               graph_count_summary, authority_status
        FROM graph_metadata
        """
    ).fetchall()
    if len(metadata_rows) > 1:
        raise ValueError(f"graphDB capability data invalid: graph_metadata_row_count={len(metadata_rows)}")
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
            raise ValueError("graphDB capability data invalid: graph_metadata summary is not an object")
        canonical_source = Path(str(materialized_from or ""))
        if not canonical_source.is_absolute():
            canonical_source = repo_root / canonical_source
        if canonical_source.is_file() and canonical_source.suffix.lower() == ".json":
            try:
                canonical_payload = json.loads(canonical_source.read_text(encoding="utf-8"))
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
                raise ValueError("graphDB capability data invalid: canonical graph source digest mismatch")
            summary.setdefault("canonical_digest_kind", "canonical_payload_v1")
        elif summary.get("canonical_digest_kind") == "canonical_payload_v1":
            raise ValueError("graphDB capability data invalid: canonical graph source is missing")
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
            "graph_index_capability_version": GRAPH_INDEX_CAPABILITY_VERSION,
            "graph_index_schema_version": GRAPH_INDEX_SCHEMA_VERSION,
            "canonical_graph_digest": str(ledger_hash),
            "sqlite_graph_digest": sqlite_graph_digest,
            "sqlite_schema_digest": sqlite_schema_digest,
            "node_count_sqlite": int(target.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0]),
            "edge_count_sqlite": int(target.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0]),
            "skill_fact_link_count": int(
                target.execute("SELECT COUNT(*) FROM skill_fact_links").fetchone()[0]
            ),
            "graph_path_count": int(target.execute("SELECT COUNT(*) FROM graph_paths").fetchone()[0]),
            "graph_neighborhood_count": int(
                target.execute("SELECT COUNT(*) FROM graph_neighborhoods").fetchone()[0]
            ),
            "graph_sibling_link_count": int(
                target.execute("SELECT COUNT(*) FROM graph_sibling_links").fetchone()[0]
            ),
            "section_evidence_budget_count": int(
                target.execute("SELECT COUNT(*) FROM section_evidence_budget").fetchone()[0]
            ),
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
    temp_path: Path | None = None
    source_snapshot_path: Path | None = None
    try:
        _require_sidecar_free_atomic_target(path)
        temp_path = _new_sibling_temp_db_path(path)
        source_snapshot_path = _new_sibling_temp_db_path(path)
    except (OSError, RuntimeError):
        if temp_path is not None:
            _cleanup_temp_sqlite(temp_path)
        if source_snapshot_path is not None:
            _cleanup_temp_sqlite(source_snapshot_path)
        _release_sqlite_maintenance_lock(maintenance_lock)
        raise
    assert temp_path is not None
    assert source_snapshot_path is not None
    source = None
    conn = None
    hardening_succeeded = False
    try:
        live_source = open_graph_sqlite(repo_root=root, db_path=path, read_only=True)
        snapshot_writer = None
        try:
            snapshot_writer = _open_isolated_temp_graph_sqlite(
                temp_path=source_snapshot_path,
                canonical_target=path,
            )
            live_source.backup(snapshot_writer)
            snapshot_writer.commit()
        finally:
            live_source.close()
            if snapshot_writer is not None:
                snapshot_writer.close()
        source = open_graph_sqlite(
            repo_root=root,
            db_path=source_snapshot_path,
            read_only=True,
        )
        conn = _open_isolated_temp_graph_sqlite(
            temp_path=temp_path,
            canonical_target=path,
        )
        for ddl in DDL_STATEMENTS:
            conn.execute(ddl)
        _validate_supported_source_schema(source, conn)
        source_authority = _validate_source_projection_authority(
            source,
            repo_root=root,
            source_path=path,
        )
        preservation_profile = _source_preservation_profile(source)
        before = {
            name: int(preservation_profile[name]["count"])
            for name in _PRESERVED_TABLES
            if name in preservation_profile
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
            raise ValueError(f"graphDB capability data invalid: broken_graph_edges={broken_graph_edges}")
        for table_name in (*_PRESERVED_TABLES, *_OPTIONAL_PRESERVED_TABLES):
            _copy_table_into_fresh_schema(source, conn, table_name)
        preservation = _verify_preserved_copy(conn, preservation_profile)
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
        after = _verify_preserved_rows_remain(conn, preservation_profile)
        preservation["final_counts"] = after
        preservation["source_rows_retained"] = True
        hardening_succeeded = True
    finally:
        if source is not None:
            source.close()
        if conn is not None:
            conn.close()
        _cleanup_temp_sqlite(source_snapshot_path)
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
        "source_authority": source_authority,
        "preservation": preservation,
        "materialization": result,
        "integrity": integrity,
        "atomic_replace": True,
    }


def main() -> None:
    print(json.dumps(apply_graphdb_capability_sqlite_hardening(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
