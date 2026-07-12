"""Read-only access to the canonical ADG repository-health contract."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import quote


def _readonly_uri(path: Path) -> str:
    return f"file:{quote(str(path.expanduser().resolve()))}?mode=ro"


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return (
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name=? LIMIT 1",
            (table,),
        ).fetchone()
        is not None
    )


def _rows_as_dicts(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    return [dict(row) for row in cursor.fetchall()]


def _source_count(conn: sqlite3.Connection, table: str) -> int | None:
    if not _table_exists(conn, table):
        return None
    row = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()
    return int(row[0]) if row is not None else 0


def _staleness_evidence(
    conn: sqlite3.Connection,
    summary: dict[str, Any],
) -> tuple[bool, list[str], dict[str, int]]:
    """Compare Phase G source counts with the currently visible canonical graph."""

    fields = {
        "source_node_count": "nodes",
        "source_edge_count": "edges",
        "source_violation_count": "violations",
    }
    reasons: list[str] = []
    current: dict[str, int] = {}
    for field, table in fields.items():
        if field not in summary:
            continue
        count = _source_count(conn, table)
        if count is None:
            reasons.append(f"{table}:missing")
            continue
        current[table] = count
        recorded = int(summary.get(field) or 0)
        if count != recorded:
            reasons.append(f"{table}:materialized={recorded},current={count}")
    return bool(reasons), reasons, current


def read_repo_health(sqlite_path: Path, *, hotspot_limit: int = 10) -> dict[str, Any]:
    """Return repo-health summary, dimensions, and top hotspots.

    Legacy snapshots without Phase G return ``available=False`` rather than
    failing the MCP health check. The database is opened in URI read-only mode
    and query-only is enabled as a second guard.
    """

    path = sqlite_path.expanduser().resolve()
    if not path.exists() or not path.is_file():
        return {
            "available": False,
            "reason": "sqlite_missing",
            "sqlite_path": str(path),
        }

    safe_limit = max(1, min(int(hotspot_limit), 100))
    try:
        with sqlite3.connect(_readonly_uri(path), uri=True, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA trusted_schema = OFF")
            conn.execute("PRAGMA query_only = ON")
            conn.execute("PRAGMA busy_timeout = 5000")
            if not _table_exists(conn, "mv_repo_health_summary"):
                return {
                    "available": False,
                    "reason": "phase_g_not_materialized",
                    "sqlite_path": str(path),
                }

            summary_row = conn.execute("SELECT * FROM mv_repo_health_summary LIMIT 1").fetchone()
            if summary_row is None:
                return {
                    "available": False,
                    "reason": "phase_g_empty",
                    "sqlite_path": str(path),
                }

            summary = dict(summary_row)
            stale, stale_reasons, current_source_counts = _staleness_evidence(conn, summary)
            summary["effective_status"] = "UNKNOWN" if stale else str(summary.get("status", "UNKNOWN"))

            dimensions = (
                _rows_as_dicts(
                    conn.execute(
                        "SELECT * FROM mv_repo_health_dimensions " "ORDER BY score ASC, dimension ASC"
                    )
                )
                if _table_exists(conn, "mv_repo_health_dimensions")
                else []
            )
            hotspots = (
                _rows_as_dicts(
                    conn.execute(
                        "SELECT * FROM mv_repo_health_hotspots "
                        "ORDER BY health_risk_score DESC, file ASC LIMIT ?",
                        (safe_limit,),
                    )
                )
                if _table_exists(conn, "mv_repo_health_hotspots")
                else []
            )
            hardening_meta: dict[str, str] = {}
            if _table_exists(conn, "meta"):
                hardening_meta = {
                    str(row["key"]): str(row["value"])
                    for row in conn.execute(
                        "SELECT key, value FROM meta "
                        "WHERE key LIKE 'sqlite_%' OR key LIKE 'repo_health_%' "
                        "ORDER BY key"
                    )
                }

            return {
                "available": True,
                "sqlite_path": str(path),
                "summary": summary,
                "stale": stale,
                "stale_reasons": stale_reasons,
                "source_counts_current": current_source_counts,
                "dimensions": dimensions,
                "top_hotspots": hotspots,
                "sqlite_hardening": hardening_meta,
            }
    except sqlite3.Error as exc:
        return {
            "available": False,
            "reason": "sqlite_query_error",
            "message": str(exc),
            "sqlite_path": str(path),
        }
