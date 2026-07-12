"""SQLite finalization for canonical ADG artifacts.

The canonical ADG is a distributable SQLite file, not a transient cache.  This
module installs query-shaped indexes, stamps the file-format contract, records
integrity evidence in ``meta``, and asks SQLite to refresh planner statistics.

It deliberately does not VACUUM on every generation: full rewrites are already
atomic and VACUUM would add avoidable wall-clock and temporary-disk pressure.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

_APPLICATION_ID: Final[int] = 0x41444731  # ASCII "ADG1", signed 32-bit safe.
_USER_VERSION: Final[int] = 2
_INDEX_CONTRACT_VERSION: Final[str] = "1"

# Query-shaped indexes for the dominant MCP, gate, and repo-health predicates.
# Each entry is (name, table, ordered columns).  Creation is conditional on the
# table/columns existing so reduced test fixtures and older snapshots remain
# materializable.
_INDEX_SPECS: Final[tuple[tuple[str, str, tuple[str, ...]], ...]] = (
    ("idx_edges_src_relation", "edges", ("src_id", "relation_type")),
    ("idx_edges_dst_relation", "edges", ("dst_id", "relation_type")),
    ("idx_edges_relation_source_line", "edges", ("relation_type", "source_file", "line_no")),
    ("idx_edges_authority_resolution", "edges", ("authority_status", "resolution_status")),
    ("idx_edges_bucket_relation", "edges", ("bucket", "relation_type")),
    ("idx_nodes_path_entity", "nodes", ("resolved_path", "entity_type")),
    ("idx_nodes_layer_entity_path", "nodes", ("layer", "entity_type", "resolved_path")),
    (
        "idx_violations_disposition_severity_category_file",
        "violations",
        ("disposition", "severity", "category", "file_path"),
    ),
    ("idx_violations_file_line_severity", "violations", ("file_path", "line_no", "severity")),
    ("idx_test_stubs_file", "test_stubs", ("file_path",)),
)


@dataclass(frozen=True)
class SQLiteHardeningReport:
    """Replayable evidence emitted by :func:`harden_sqlite_connection`."""

    quick_check: str
    foreign_key_violation_count: int
    page_count: int
    freelist_count: int
    index_count: int
    application_id: int
    user_version: int
    indexes_created: int
    index_contract_version: str = _INDEX_CONTRACT_VERSION

    def as_meta(self) -> dict[str, str]:
        """Return values in the string form expected by the ADG ``meta`` table."""

        payload = asdict(self)
        return {f"sqlite_{key}": str(value) for key, value in payload.items()}


@dataclass(frozen=True)
class SQLiteSealReport:
    """Evidence that the WAL-backed build was sealed as one portable file."""

    quick_check: str
    journal_mode: str
    wal_busy: int
    wal_log_frames: int
    wal_checkpointed_frames: int
    application_id: int
    user_version: int


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """Return columns for ``table`` or an empty set when the table is absent."""

    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone()
    if exists is None:
        return set()
    return {str(row[1]) for row in conn.execute(f'PRAGMA table_info("{table}")')}


def _install_query_indexes(conn: sqlite3.Connection) -> int:
    """Create every compatible query-shaped index and return the new-index count."""

    before = {
        str(row[0])
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_autoindex_%'"
        )
    }
    for name, table, columns in _INDEX_SPECS:
        available = _table_columns(conn, table)
        if not set(columns).issubset(available):
            continue
        column_sql = ", ".join(f'"{column}"' for column in columns)
        conn.execute(f'CREATE INDEX IF NOT EXISTS "{name}" ON "{table}" ({column_sql})')

    after = {
        str(row[0])
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_autoindex_%'"
        )
    }
    return len(after - before)


def _upsert_meta(conn: sqlite3.Connection, values: dict[str, str]) -> None:
    """Persist hardening evidence when the canonical ``meta`` table is present."""

    if not _table_columns(conn, "meta").issuperset({"key", "value"}):
        return
    conn.executemany(
        "INSERT INTO meta(key, value) VALUES (?, ?) " "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        sorted(values.items()),
    )


def _strict_foreign_keys_enabled() -> bool:
    return os.environ.get("ADG_STRICT_FOREIGN_KEYS", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def harden_sqlite_connection(
    conn: sqlite3.Connection,
    *,
    strict_foreign_keys: bool | None = None,
) -> SQLiteHardeningReport:
    """Finalize a canonical ADG SQLite connection for reliable read consumers.

    The caller must provide a writable connection outside an active transaction.
    Structural corruption always raises. Existing foreign-key violations are
    recorded and become a repo-health signal; set ``ADG_STRICT_FOREIGN_KEYS=1``
    (or pass ``strict_foreign_keys=True``) to promote them to a hard failure.
    """

    if conn.in_transaction:
        conn.commit()

    conn.execute("PRAGMA trusted_schema = OFF")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    indexes_created = _install_query_indexes(conn)
    conn.execute(f"PRAGMA application_id = {_APPLICATION_ID}")
    conn.execute(f"PRAGMA user_version = {_USER_VERSION}")
    conn.commit()

    quick_rows = [str(row[0]) for row in conn.execute("PRAGMA quick_check")]
    quick_check = "ok" if quick_rows == ["ok"] else "; ".join(quick_rows)
    if quick_check != "ok":
        raise RuntimeError(f"SQLite quick_check failed: {quick_check}")

    foreign_key_rows = list(conn.execute("PRAGMA foreign_key_check"))
    foreign_key_violation_count = len(foreign_key_rows)

    # SQLite recommends PRAGMA optimize after schema/index changes.  It is
    # normally a no-op and applies a bounded analysis limit when work is needed.
    conn.execute("PRAGMA optimize")

    page_count = int(conn.execute("PRAGMA page_count").fetchone()[0])
    freelist_count = int(conn.execute("PRAGMA freelist_count").fetchone()[0])
    index_count = int(
        conn.execute(
            "SELECT COUNT(*) FROM sqlite_master " "WHERE type='index' AND name NOT LIKE 'sqlite_autoindex_%'"
        ).fetchone()[0]
    )
    application_id = int(conn.execute("PRAGMA application_id").fetchone()[0])
    user_version = int(conn.execute("PRAGMA user_version").fetchone()[0])

    report = SQLiteHardeningReport(
        quick_check=quick_check,
        foreign_key_violation_count=foreign_key_violation_count,
        page_count=page_count,
        freelist_count=freelist_count,
        index_count=index_count,
        application_id=application_id,
        user_version=user_version,
        indexes_created=indexes_created,
    )
    meta = report.as_meta()
    meta["sqlite_optimizer"] = "pragma_optimize"
    meta["sqlite_hardening_contract"] = "adg-sqlite-v2"
    _upsert_meta(conn, meta)
    conn.commit()

    strict = _strict_foreign_keys_enabled() if strict_foreign_keys is None else strict_foreign_keys
    if strict and foreign_key_violation_count:
        sample = foreign_key_rows[:5]
        raise RuntimeError(
            "SQLite foreign_key_check failed: "
            f"{foreign_key_violation_count} violation(s); sample={sample!r}"
        )

    return report


def seal_sqlite_connection(conn: sqlite3.Connection) -> SQLiteSealReport:
    """Checkpoint every committed WAL frame into the portable main database.

    WAL remains the concurrency policy for future generator/read sessions, but a
    published snapshot must not require an unshipped ``-wal`` sidecar to contain
    its committed truth.  ``TRUNCATE`` provides that boundary. A blocked
    checkpoint is a hard failure rather than a misleadingly complete artifact.
    """

    if conn.in_transaction:
        conn.commit()

    conn.execute("PRAGMA trusted_schema = OFF")
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA synchronous = FULL")
    quick_rows = [str(row[0]) for row in conn.execute("PRAGMA quick_check")]
    quick_check = "ok" if quick_rows == ["ok"] else "; ".join(quick_rows)
    if quick_check != "ok":
        raise RuntimeError(f"SQLite final quick_check failed: {quick_check}")

    checkpoint_row = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    wal_busy, wal_log_frames, wal_checkpointed_frames = (
        tuple(int(value) for value in checkpoint_row) if checkpoint_row is not None else (0, -1, -1)
    )
    if wal_busy:
        raise RuntimeError(
            "SQLite WAL seal failed: checkpoint remained busy "
            f"(log={wal_log_frames}, checkpointed={wal_checkpointed_frames})"
        )

    mode_row = conn.execute("PRAGMA journal_mode").fetchone()
    journal_mode = str(mode_row[0]).lower() if mode_row else ""
    report = SQLiteSealReport(
        quick_check=quick_check,
        journal_mode=journal_mode,
        wal_busy=wal_busy,
        wal_log_frames=wal_log_frames,
        wal_checkpointed_frames=wal_checkpointed_frames,
        application_id=int(conn.execute("PRAGMA application_id").fetchone()[0]),
        user_version=int(conn.execute("PRAGMA user_version").fetchone()[0]),
    )
    _upsert_meta(
        conn,
        {
            "sqlite_final_quick_check": report.quick_check,
            "sqlite_sealed_journal_mode": report.journal_mode,
            "sqlite_wal_checkpoint_busy": str(report.wal_busy),
            "sqlite_wal_log_frames": str(report.wal_log_frames),
            "sqlite_wal_checkpointed_frames": str(report.wal_checkpointed_frames),
            "sqlite_seal_contract": "wal-checkpointed-main-db-v1",
        },
    )
    conn.commit()
    return report


def seal_sqlite_path(sqlite_path: Path, *, timeout: float = 30.0) -> SQLiteSealReport:
    """Open, verify, and seal a concrete SQLite artifact by path.

    This is used at the graph-projection boundary after all optional enrichment
    and authority backfills, ensuring those late writes are present in the main
    database before downstream gates or artifact packaging consume it.
    """

    path = sqlite_path.expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"ADG SQLite not found: {path}")
    with sqlite3.connect(str(path), timeout=timeout) as conn:
        conn.execute(f"PRAGMA busy_timeout = {max(1, int(timeout * 1000))}")
        return seal_sqlite_connection(conn)
