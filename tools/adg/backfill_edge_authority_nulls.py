"""Backfill the closed-enum columns on edges where they are NULL.

Plan: ``.windsurf/plans/three-bucket-gap-remediation-069806.md`` (W7 follow-up).

The supplementary scanners (gate_self_test, entrypoint, r6) sometimes
emit rows AFTER the canonical edge_authority backfill runs in
``generate_full_adg.py``. When that final backfill stage is skipped
(e.g., upstream try/except short-circuits), those rows ship with
``authority``/``bucket``/``resolution_status``/``authority_status`` NULL
and block the W7 NOT NULL graduation.

This script is idempotent: it runs the canonical backfill SQL from
``agentic_core.adg.artifact.edge_authority`` against any snapshot, NULL
or not. Safe to run repeatedly. After running, ``check_schema_graduation_readiness.py``
reports zero blockers and graduation can proceed.

Usage::

    python tools/adg/backfill_edge_authority_nulls.py
    python tools/adg/backfill_edge_authority_nulls.py --snapshot path/to/.sqlite
    python tools/adg/backfill_edge_authority_nulls.py --dry-run
"""

from __future__ import annotations

# Direct SQLite write — read-modify-write of canonical snapshot. Not an ADG
# consumer (no MV reads) but writes to the canonical store, so declare proof.
__adg_consumer_mode__ = "proof"

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR: Final[Path] = REPO_ROOT / "artifacts" / "adg"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.artifact.edge_authority import (  # noqa: E402
    SQL_AUTHORITY_BACKFILL,
    SQL_TRIPLET_BACKFILL,
)


@dataclass
class BackfillStats:
    snapshot: str = ""
    null_authority_before: int = 0
    null_bucket_before: int = 0
    null_authority_after: int = 0
    null_bucket_after: int = 0
    rows_authority_updated: int = 0
    rows_triplet_updated: int = 0
    dry_run: bool = False


def _latest_snapshot() -> Path | None:
    snaps = sorted(ARTIFACTS_DIR.glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


def _count_nulls(con: sqlite3.Connection) -> tuple[int, int]:
    a = con.execute("SELECT COUNT(*) FROM edges WHERE authority IS NULL").fetchone()[0]
    b = con.execute(
        "SELECT COUNT(*) FROM edges WHERE bucket IS NULL "
        "OR resolution_status IS NULL OR authority_status IS NULL"
    ).fetchone()[0]
    return int(a), int(b)


def backfill(snapshot: Path, *, dry_run: bool = False) -> BackfillStats:
    if not snapshot.exists():
        raise FileNotFoundError(f"snapshot not found: {snapshot}")
    stats = BackfillStats(snapshot=str(snapshot), dry_run=dry_run)

    con = sqlite3.connect(str(snapshot))
    try:
        before_authority, before_triplet = _count_nulls(con)
        stats.null_authority_before = before_authority
        stats.null_bucket_before = before_triplet

        # Idempotent: SQL_AUTHORITY_BACKFILL only updates rows where
        # authority IS NULL; SQL_TRIPLET_BACKFILL only updates rows where
        # any of the triplet columns are NULL.
        cur = con.execute(SQL_AUTHORITY_BACKFILL)
        stats.rows_authority_updated = cur.rowcount or 0
        cur = con.execute(SQL_TRIPLET_BACKFILL)
        stats.rows_triplet_updated = cur.rowcount or 0

        after_authority, after_triplet = _count_nulls(con)
        stats.null_authority_after = after_authority
        stats.null_bucket_after = after_triplet

        if dry_run:
            con.rollback()
        else:
            con.commit()
    finally:
        con.close()

    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    snap = args.snapshot or _latest_snapshot()
    if snap is None:
        print("[backfill_edge_authority_nulls] FAIL: no snapshot found")
        return 1

    stats = backfill(snap, dry_run=args.dry_run)

    print(f"[backfill] snapshot                = {stats.snapshot}")
    print(f"[backfill] dry_run                 = {stats.dry_run}")
    print(f"[backfill] null_authority_before   = {stats.null_authority_before}")
    print(f"[backfill] null_bucket_before      = {stats.null_bucket_before}")
    print(f"[backfill] rows_authority_updated  = {stats.rows_authority_updated}")
    print(f"[backfill] rows_triplet_updated    = {stats.rows_triplet_updated}")
    print(f"[backfill] null_authority_after    = {stats.null_authority_after}")
    print(f"[backfill] null_bucket_after       = {stats.null_bucket_after}")

    if not args.dry_run and (stats.null_authority_after or stats.null_bucket_after):
        print("[backfill] WARNING: NULL rows remain after backfill")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
