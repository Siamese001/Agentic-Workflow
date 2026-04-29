"""Schema graduation: ALTER edges.{bucket,resolution_status,authority_status,authority}
to NOT NULL (W7 of plan three-bucket-gap-remediation-069806).

This is the **mechanism**, not the trigger. The ACTUAL graduation (running
this script with --commit) is gated on a 4-week green window in which:

  * 3B1 runtime proof view well-formed   = OK every regen
  * 3B2 OTel GenAI semconv coverage      = >= 80% every regen
  * 3B3 three-bucket gap thresholds      = OK every regen
  * 3B4 ADG snapshot signed              = verified every regen

Once that window closes cleanly, ops invokes::

    python tools/adg/graduate_schema_not_null.py --commit

Until then, the script is a no-op safety check that reports remaining
NULL counts and identifies which rows would block migration.

How the migration works (SQLite NOT NULL graduation pattern):
  SQLite does not support ``ALTER COLUMN ... SET NOT NULL`` directly.
  We use the canonical "rename + create + copy + drop + rename" recipe:

    1. Verify zero NULL rows in target columns (else REFUSE).
    2. CREATE TABLE edges_new with NOT NULL on the target columns.
    3. INSERT INTO edges_new SELECT * FROM edges.
    4. DROP TABLE edges; ALTER TABLE edges_new RENAME TO edges.
    5. Re-create any indexes that referenced edges.
    6. ANALYZE / VACUUM (optional, leaves to ops).

The script is idempotent: when columns are already NOT NULL it reports
"already graduated" and exits 0.

Bypass: ``SCHEMA_GRADUATION_BYPASS=1``.
"""

from __future__ import annotations

# This script consumes the snapshot via direct SQLite; it does not query
# ADG materialized views.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR: Final[Path] = REPO_ROOT / "artifacts" / "adg"
GRADUATION_REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "schema_graduation_report.json"
)

# Columns to graduate. Order matters only for the CREATE TABLE definition.
TARGET_COLUMNS: Final[tuple[str, ...]] = (
    "bucket",
    "resolution_status",
    "authority_status",
    "authority",
)


@dataclass
class GraduationStats:
    snapshot: str = ""
    timestamp: str = ""
    target_columns: list[str] = field(default_factory=list)
    null_counts: dict[str, int] = field(default_factory=dict)
    already_graduated: list[str] = field(default_factory=list)
    needs_graduation: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    committed: bool = False
    dry_run: bool = True
    status: str = "ok"


def _latest_snapshot() -> Path | None:
    snaps = sorted(ARTIFACTS_DIR.glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


def _column_info(con: sqlite3.Connection, table: str) -> dict[str, dict]:
    """Return {colname: {type, notnull, dflt_value}} from PRAGMA table_info."""
    info: dict[str, dict] = {}
    for row in con.execute(f"PRAGMA table_info({table})").fetchall():
        info[row[1]] = {"type": row[2], "notnull": row[3], "dflt": row[4]}
    return info


def _null_count(con: sqlite3.Connection, table: str, col: str) -> int:
    return int(con.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL"
    ).fetchone()[0])


def assess(snapshot: Path) -> GraduationStats:
    """Inspect the snapshot. Pure: no mutation."""
    stats = GraduationStats(
        snapshot=str(snapshot.relative_to(REPO_ROOT))
        if snapshot.is_relative_to(REPO_ROOT) else str(snapshot),
        timestamp=datetime.now(timezone.utc).isoformat(),
        target_columns=list(TARGET_COLUMNS),
        dry_run=True,
    )
    con = sqlite3.connect(str(snapshot))
    try:
        info = _column_info(con, "edges")
        for col in TARGET_COLUMNS:
            if col not in info:
                stats.blockers.append(f"column '{col}' not present in edges table")
                continue
            if info[col]["notnull"] == 1:
                stats.already_graduated.append(col)
            else:
                stats.needs_graduation.append(col)
            n_null = _null_count(con, "edges", col)
            stats.null_counts[col] = n_null
            if n_null > 0:
                stats.blockers.append(
                    f"column '{col}' has {n_null} NULL rows; backfill before graduation"
                )
    finally:
        con.close()
    if stats.blockers:
        stats.status = "blocked"
    elif not stats.needs_graduation:
        stats.status = "already_graduated"
    else:
        stats.status = "ready"
    return stats


def _build_indexes(con: sqlite3.Connection) -> list[str]:
    """Capture the SQL of every index on edges so we can recreate after rename."""
    rows = con.execute(
        "SELECT sql FROM sqlite_master "
        "WHERE type='index' AND tbl_name='edges' AND sql IS NOT NULL"
    ).fetchall()
    return [r[0] for r in rows]


def _build_dependent_views(con: sqlite3.Connection) -> list[tuple[str, str]]:
    """Capture (name, sql) for every view in the database.

    Why ALL views, not just those that mention 'edges': SQLite views can
    transitively depend on other views (e.g., `v_infra_violations_summary`
    selects from `v_p0_l0_raw_execution`). Dropping only direct-dependents
    before the rename leaves intermediate views referencing now-vanished
    intermediate views. The clean recipe is drop-all → swap-table →
    recreate-all. SQLite resolves view-to-object references at QUERY
    time, so recreation order does not matter.
    """
    rows = con.execute(
        "SELECT name, sql FROM sqlite_master "
        "WHERE type='view' AND sql IS NOT NULL "
        "ORDER BY name"
    ).fetchall()
    return [(r[0], r[1]) for r in rows if r[1]]


def graduate(snapshot: Path) -> GraduationStats:
    """Perform the SQLite NOT NULL graduation. CALLER guarantees stats.status='ready'."""
    stats = assess(snapshot)
    if stats.status != "ready":
        return stats  # caller already knows how to interpret 'blocked'/'already_graduated'

    stats.dry_run = False
    con = sqlite3.connect(str(snapshot))
    try:
        con.execute("BEGIN")
        indexes = _build_indexes(con)
        dependent_views = _build_dependent_views(con)
        info = _column_info(con, "edges")

        # Drop dependent views BEFORE rename (SQLite resolves view-to-table
        # references at execute time; the rename would break them).
        for view_name, _view_sql in dependent_views:
            con.execute(f"DROP VIEW IF EXISTS {view_name}")

        # Build the new column definition list, applying NOT NULL to TARGET_COLUMNS.
        col_defs: list[str] = []
        for col, meta in info.items():
            base = f"{col} {meta['type']}"
            if col in TARGET_COLUMNS or meta["notnull"] == 1:
                base += " NOT NULL"
            if meta["dflt"] is not None:
                base += f" DEFAULT {meta['dflt']}"
            if col == "id":
                base = "id INTEGER PRIMARY KEY AUTOINCREMENT"
            col_defs.append(base)

        # Create the new table.
        con.execute(f"CREATE TABLE edges_new ({', '.join(col_defs)})")

        # Copy rows. Using SELECT * FROM edges preserves column order.
        cols = ", ".join(info.keys())
        con.execute(f"INSERT INTO edges_new ({cols}) SELECT {cols} FROM edges")

        # Swap.
        con.execute("DROP TABLE edges")
        con.execute("ALTER TABLE edges_new RENAME TO edges")

        # Recreate indexes.
        for idx_sql in indexes:
            try:
                con.execute(idx_sql)
            except sqlite3.OperationalError as exc:
                stats.blockers.append(f"index recreate failed: {exc}")

        # Recreate dependent views (idempotent — DROP IF EXISTS first to be safe).
        for view_name, view_sql in dependent_views:
            try:
                con.execute(f"DROP VIEW IF EXISTS {view_name}")
                con.execute(view_sql)
            except sqlite3.OperationalError as exc:
                stats.blockers.append(f"view recreate failed for {view_name}: {exc}")

        if stats.blockers:
            con.execute("ROLLBACK")
            stats.status = "rolled_back"
            return stats
        con.execute("COMMIT")
        stats.committed = True
        stats.status = "graduated"
    finally:
        con.close()
    # Post-graduation re-assessment to confirm.
    post = assess(snapshot)
    stats.already_graduated = list(post.already_graduated)
    stats.needs_graduation = list(post.needs_graduation)
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Actually perform the graduation (default: dry-run / report only)",
    )
    args = parser.parse_args(argv)

    if os.environ.get("SCHEMA_GRADUATION_BYPASS") == "1":
        print("[graduate_schema] bypass active (SCHEMA_GRADUATION_BYPASS=1)")
        return 0

    snapshot = args.snapshot or _latest_snapshot()
    if snapshot is None:
        print("[graduate_schema] FAIL: no snapshot found")
        return 1

    stats = assess(snapshot) if not args.commit else graduate(snapshot)

    GRADUATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    GRADUATION_REPORT_PATH.write_text(
        json.dumps(asdict(stats), indent=2), encoding="utf-8"
    )

    print(f"[graduate_schema] snapshot         = {stats.snapshot}")
    print(f"[graduate_schema] status           = {stats.status}")
    print(f"[graduate_schema] already          = {stats.already_graduated}")
    print(f"[graduate_schema] needs_graduation = {stats.needs_graduation}")
    print(f"[graduate_schema] blockers         = {len(stats.blockers)}")
    for b in stats.blockers:
        print(f"  - {b}")
    print(f"[graduate_schema] committed        = {stats.committed}")
    print(f"[graduate_schema] report           = {GRADUATION_REPORT_PATH.relative_to(REPO_ROOT)}")

    if stats.status in ("graduated", "already_graduated", "ready"):
        return 0
    if stats.status in ("blocked", "rolled_back"):
        return 1 if args.commit else 0  # advisory in dry-run
    return 0


if __name__ == "__main__":
    sys.exit(main())
