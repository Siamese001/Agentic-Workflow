"""Tests for tools/adg/graduate_schema_not_null.py +
ops_scripts/ci/check_schema_graduation_readiness.py (W7).

Plan: ``.windsurf/plans/three-bucket-gap-remediation-069806.md`` (W7).
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_schema_graduation_readiness.py"

__adg_consumer_mode__ = "inventory"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _build_snapshot_with_nullable_columns(path: Path, *, with_nulls: bool) -> None:
    """Build a minimal edges table with nullable closed-enum columns."""
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT NOT NULL,
            source_file TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            symbol TEXT NOT NULL DEFAULT '',
            authority TEXT,
            bucket TEXT,
            resolution_status TEXT,
            authority_status TEXT,
            evidence_refs TEXT
        );
        CREATE INDEX idx_edges_src ON edges(src_id);
        """
    )
    if with_nulls:
        # 1 row with all enum cols NULL.
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, "
            "source_file, line_no) VALUES (1, 2, 'imports', 'static', 'a.py', 10)"
        )
    # 2 rows fully populated.
    for _ in range(2):
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, "
            "source_file, line_no, authority, bucket, resolution_status, "
            "authority_status) VALUES (1, 2, 'imports', 'static', 'a.py', 10, "
            "'verified', 'static', 'authority_resolved', 'AUTHORITATIVE_STATIC')"
        )
    con.commit()
    con.close()


@pytest.fixture
def tmp_snapshot_with_nulls(tmp_path: Path) -> Path:
    snap = tmp_path / "with_nulls.sqlite"
    _build_snapshot_with_nullable_columns(snap, with_nulls=True)
    return snap


@pytest.fixture
def tmp_snapshot_clean(tmp_path: Path) -> Path:
    snap = tmp_path / "clean.sqlite"
    _build_snapshot_with_nullable_columns(snap, with_nulls=False)
    return snap


# ---------------------------------------------------------------------------
# assess() — pure, no mutation
# ---------------------------------------------------------------------------


class TestAssess:
    def test_blocked_when_nulls_remain(self, tmp_snapshot_with_nulls: Path):
        from tools.adg.graduate_schema_not_null import assess  # noqa: PLC0415

        stats = assess(tmp_snapshot_with_nulls)
        assert stats.status == "blocked"
        assert len(stats.blockers) == 4  # 4 columns, each with 1 NULL row
        assert stats.null_counts["bucket"] == 1
        assert stats.committed is False

    def test_ready_when_no_nulls(self, tmp_snapshot_clean: Path):
        from tools.adg.graduate_schema_not_null import assess  # noqa: PLC0415

        stats = assess(tmp_snapshot_clean)
        assert stats.status == "ready"
        assert not stats.blockers
        assert stats.null_counts == {
            "bucket": 0, "resolution_status": 0,
            "authority_status": 0, "authority": 0,
        }

    def test_already_graduated_when_columns_are_not_null(self, tmp_path: Path):
        snap = tmp_path / "graduated.sqlite"
        con = sqlite3.connect(snap)
        con.executescript(
            """
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_id INTEGER NOT NULL,
                dst_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                edge_kind TEXT NOT NULL,
                source_file TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                symbol TEXT NOT NULL DEFAULT '',
                authority TEXT NOT NULL,
                bucket TEXT NOT NULL,
                resolution_status TEXT NOT NULL,
                authority_status TEXT NOT NULL,
                evidence_refs TEXT
            );
            """
        )
        con.commit()
        con.close()
        from tools.adg.graduate_schema_not_null import assess  # noqa: PLC0415

        stats = assess(snap)
        assert stats.status == "already_graduated"
        assert sorted(stats.already_graduated) == [
            "authority", "authority_status", "bucket", "resolution_status"
        ]


# ---------------------------------------------------------------------------
# graduate() — mutation; verify on a clean snapshot
# ---------------------------------------------------------------------------


class TestGraduate:
    def test_graduate_succeeds_on_clean_snapshot(
        self, tmp_snapshot_clean: Path
    ):
        from tools.adg.graduate_schema_not_null import graduate  # noqa: PLC0415

        stats = graduate(tmp_snapshot_clean)
        assert stats.status == "graduated"
        assert stats.committed is True

        # Confirm columns are now NOT NULL on disk.
        con = sqlite3.connect(tmp_snapshot_clean)
        try:
            info = {
                row[1]: row[3]
                for row in con.execute("PRAGMA table_info(edges)").fetchall()
            }
        finally:
            con.close()
        assert info["bucket"] == 1
        assert info["resolution_status"] == 1
        assert info["authority_status"] == 1
        assert info["authority"] == 1

    def test_graduate_refuses_when_blocked(
        self, tmp_snapshot_with_nulls: Path
    ):
        from tools.adg.graduate_schema_not_null import graduate  # noqa: PLC0415

        stats = graduate(tmp_snapshot_with_nulls)
        # graduate() short-circuits when assess() returns 'blocked'.
        assert stats.status == "blocked"
        assert stats.committed is False

    def test_graduate_is_idempotent(self, tmp_snapshot_clean: Path):
        from tools.adg.graduate_schema_not_null import graduate  # noqa: PLC0415

        stats1 = graduate(tmp_snapshot_clean)
        assert stats1.status == "graduated"
        # Second call should report already_graduated and not re-run the
        # migration.
        stats2 = graduate(tmp_snapshot_clean)
        assert stats2.status == "already_graduated"
        assert stats2.committed is False

    def test_graduate_preserves_row_data(self, tmp_snapshot_clean: Path):
        from tools.adg.graduate_schema_not_null import graduate  # noqa: PLC0415

        con = sqlite3.connect(tmp_snapshot_clean)
        try:
            n_before = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        finally:
            con.close()
        graduate(tmp_snapshot_clean)
        con = sqlite3.connect(tmp_snapshot_clean)
        try:
            n_after = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        finally:
            con.close()
        assert n_before == n_after

    def test_graduate_recreates_indexes(self, tmp_snapshot_clean: Path):
        from tools.adg.graduate_schema_not_null import graduate  # noqa: PLC0415

        graduate(tmp_snapshot_clean)
        con = sqlite3.connect(tmp_snapshot_clean)
        try:
            indexes = [
                row[0]
                for row in con.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='index' AND tbl_name='edges'"
                ).fetchall()
            ]
        finally:
            con.close()
        assert "idx_edges_src" in indexes


# ---------------------------------------------------------------------------
# CI gate
# ---------------------------------------------------------------------------


def _run_gate(*args: str, env: dict | None = None) -> tuple[int, str]:
    cmd = [sys.executable, str(GATE), *args]
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, env=full_env, check=False
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestGate:
    def test_gate_advisory_does_not_block_on_blockers(
        self, tmp_snapshot_with_nulls: Path
    ):
        rc, out = _run_gate("--snapshot", str(tmp_snapshot_with_nulls))
        assert rc == 0
        assert "status=blocked" in out
        assert "blockers=4" in out

    def test_gate_strict_blocks_on_blockers(
        self, tmp_snapshot_with_nulls: Path
    ):
        rc, out = _run_gate(
            "--snapshot", str(tmp_snapshot_with_nulls), "--strict"
        )
        assert rc == 1
        assert "status=blocked" in out

    def test_gate_passes_when_clean(self, tmp_snapshot_clean: Path):
        rc, out = _run_gate(
            "--snapshot", str(tmp_snapshot_clean), "--strict"
        )
        assert rc == 0
        assert "status=ready" in out

    def test_gate_bypass_short_circuits(self, tmp_snapshot_with_nulls: Path):
        rc, out = _run_gate(
            "--snapshot", str(tmp_snapshot_with_nulls), "--strict",
            env={"SCHEMA_GRADUATION_READINESS_BYPASS": "1"},
        )
        assert rc == 0
        assert "bypass active" in out


# W6 P6.3 completion-audit (2026-04-30): the graduator's internal
# _latest_snapshot() had the same naive sorted(glob())[-1] bug as the
# P6.1 gates. Fixed to delegate to the canonical resolver. This test
# pins that fix so a future refactor can't regress it.
class TestGraduatorSnapshotResolver:
    def test_latest_snapshot_skips_sentinel(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """_latest_snapshot must skip adg_indexed_99999999_9999.sqlite."""
        art = tmp_path / "artifacts" / "adg"
        art.mkdir(parents=True)
        real = art / "adg_indexed_04302026_1319.sqlite"
        sentinel = art / "adg_indexed_99999999_9999.sqlite"
        # Minimal valid SQLite for real; empty-ish stub for sentinel.
        sqlite3.connect(real).close()
        sqlite3.connect(sentinel).close()

        monkeypatch.setenv("ADG_DIR", str(art))
        import tools.adg.graduate_schema_not_null as grad  # noqa: PLC0415
        import importlib  # noqa: PLC0415
        importlib.reload(grad)

        resolved = grad._latest_snapshot()
        assert resolved is not None
        assert resolved.name == "adg_indexed_04302026_1319.sqlite", (
            f"graduator resolver shadowed by sentinel; got {resolved.name!r}"
        )
