"""Tests for tools/adg/backfill_edge_authority_nulls.py.

Plan: docs/archive/windsurf/legacy-tree/plans/three-bucket-gap-remediation-069806.md (W7 follow-up).

Verifies:
  * Idempotent backfill — running on a fully-populated snapshot is a no-op.
  * NULL rows get authority filled by SQL_AUTHORITY_BACKFILL.
  * After authority fill, SQL_TRIPLET_BACKFILL fans out into bucket /
    resolution_status / authority_status.
  * Dry-run rolls back; commit persists.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.backfill_edge_authority_nulls import backfill  # noqa: E402


def _build_snapshot_with_nulls(path: Path, n_null_rows: int = 5) -> None:
    """Build a synthetic ADG snapshot with N null-authority edges."""
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL,
            resolved_path TEXT
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            dynamic_resolution TEXT,
            authority TEXT,
            bucket TEXT,
            resolution_status TEXT,
            authority_status TEXT,
            evidence_refs TEXT
        );
        """
    )
    # Two nodes — src module, dst gate-self-test virtual node (mirrors the
    # real-world 32-NULL gate_self_test pattern)
    con.execute(
        "INSERT INTO nodes (adg_name, resolved_path) VALUES "
        "('ADG::Module::ops_scripts/ci/check_x.py', 'ops_scripts/ci/check_x.py')"
    )
    con.execute(
        "INSERT INTO nodes (adg_name, resolved_path) VALUES "
        "('ADG::GateSelfTest::enforcement_without_claim', '')"
    )
    # Insert N rows with authority NULL (mirroring the supplementary
    # gate_self_test scanner emitting after the canonical backfill).
    for _ in range(n_null_rows):
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, "
            "source_file) VALUES (1, 2, 'gate_self_test', 'enforcement', "
            "'ops_scripts/ci/check_x.py')"
        )
    # Insert one already-populated row to verify backfill is idempotent.
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, "
        "source_file, authority, bucket, resolution_status, authority_status) "
        "VALUES (1, 2, 'imports', 'static', 'src.py', "
        "'verified', 'static', 'VERIFIED_MODULE', 'AUTHORITATIVE')"
    )
    con.commit()
    con.close()


@pytest.fixture
def snapshot_with_nulls(tmp_path: Path) -> Path:
    snap = tmp_path / "snap.sqlite"
    _build_snapshot_with_nulls(snap, n_null_rows=5)
    return snap


@pytest.fixture
def already_populated_snapshot(tmp_path: Path) -> Path:
    snap = tmp_path / "snap_clean.sqlite"
    _build_snapshot_with_nulls(snap, n_null_rows=0)
    return snap


# ---------------------------------------------------------------------------
# Backfill mechanics
# ---------------------------------------------------------------------------


class TestBackfill:
    def test_fills_null_authority_rows(self, snapshot_with_nulls: Path):
        stats = backfill(snapshot_with_nulls)
        assert stats.null_authority_before == 5
        assert stats.null_authority_after == 0
        assert stats.rows_authority_updated == 5

    def test_fans_into_triplet_columns(self, snapshot_with_nulls: Path):
        backfill(snapshot_with_nulls)
        con = sqlite3.connect(snapshot_with_nulls)
        try:
            n_null_bucket = con.execute(
                "SELECT COUNT(*) FROM edges WHERE bucket IS NULL"
            ).fetchone()[0]
            n_null_resolution = con.execute(
                "SELECT COUNT(*) FROM edges WHERE resolution_status IS NULL"
            ).fetchone()[0]
            n_null_authority_status = con.execute(
                "SELECT COUNT(*) FROM edges WHERE authority_status IS NULL"
            ).fetchone()[0]
        finally:
            con.close()
        assert n_null_bucket == 0
        assert n_null_resolution == 0
        assert n_null_authority_status == 0

    def test_idempotent_on_clean_snapshot(self, already_populated_snapshot: Path):
        stats = backfill(already_populated_snapshot)
        assert stats.null_authority_before == 0
        assert stats.null_authority_after == 0
        # Running again is also a no-op.
        stats2 = backfill(already_populated_snapshot)
        assert stats2.null_authority_after == 0

    def test_dry_run_rolls_back(self, snapshot_with_nulls: Path):
        stats = backfill(snapshot_with_nulls, dry_run=True)
        # Stats reflect what WOULD have happened
        assert stats.dry_run is True
        # But the file itself still has 5 null rows
        con = sqlite3.connect(snapshot_with_nulls)
        try:
            n_null = con.execute(
                "SELECT COUNT(*) FROM edges WHERE authority IS NULL"
            ).fetchone()[0]
        finally:
            con.close()
        assert n_null == 5

    def test_does_not_modify_already_populated_rows(
        self, snapshot_with_nulls: Path
    ):
        backfill(snapshot_with_nulls)
        # The seeded "verified / static / VERIFIED_MODULE / AUTHORITATIVE"
        # row should remain unchanged.
        con = sqlite3.connect(snapshot_with_nulls)
        try:
            row = con.execute(
                "SELECT authority, bucket, resolution_status, authority_status "
                "FROM edges WHERE relation_type='imports'"
            ).fetchone()
        finally:
            con.close()
        assert row == ("verified", "static", "VERIFIED_MODULE", "AUTHORITATIVE")

    def test_raises_on_missing_snapshot(self, tmp_path: Path):
        nonexistent = tmp_path / "missing.sqlite"
        with pytest.raises(FileNotFoundError):
            backfill(nonexistent)
