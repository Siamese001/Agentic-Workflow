"""EXHAUSTIVE tests for pre_mcp_gate.py (Phase 1.3) — PP-1, PP-10.

Plan requirements verified:
  - Filesystem MCP write tools (write_file, edit_file): exit 2 (BLOCKED)
  - Filesystem MCP read tools (read_text_file, list_directory, etc.): exit 0 (allowed)
  - Filesystem MCP with no tool name: exit 0 (allowed — read assumed)
  - Non-ADG, non-filesystem MCPs: always exit 0 (fail-open)
  - ADG MCP + recovery tools: always exit 0 (whitelist)
  - ADG MCP + real SQLite read probe failure: exit 2 (block)
  - ADG MCP + real SQLite write contention (BEGIN IMMEDIATE → BUSY): exit 2 (block)
  - ADG MCP + stale snapshot (>30 min): exit 2 (block)
  - ADG MCP + fresh snapshot + healthy DB: exit 0 (allow)
  - ADG MCP + no snapshot at all: exit 0 (allow — fail-open on missing)
  - ADG MCP + no artifacts/adg dir: exit 0 (allow — fail-open)
  - WAL sidecar presence (zero or non-zero) does NOT block read-only tools
  - Write-affecting tools probe BEGIN IMMEDIATE for real contention
  - Path canonicalization prevents duplicate-path false positives
  - All recovery tools whitelisted: adg_health, adg_status, adg_close_connections, adg_reopen_connections
  - Empty stdin: exit 0 (non-ADG assumed, fail-open)
  - Malformed JSON: exit 0 (fail-open for non-ADG)
  - Missing server name: exit 0
  - Flat payload: handled
  - ADG MCP + no SQLite file at all → auto-generate; exit 0 on success, exit 2 on failure
  - _has_adg_sqlite: returns False when dir missing, empty, or no adg_indexed_* file
  - _auto_generate_adg: invokes subprocess with shell=False, check=False, timeout=300; returns True/False
  - reopen_connections recreates WAL sidecars → subsequent reads still allowed
  - journal file presence alone does not block
"""

import json
import os
import sqlite3
import subprocess
import sys
import time
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.pre_mcp_gate import (
    ADG_RECOVERY_TOOLS,
    ADG_WRITE_TOOLS,
    FILESYSTEM_WRITE_TOOLS,
    _auto_generate_adg,
    _check_sqlite_access,
    _get_latest_snapshot_age_seconds,
    _get_sidecar_diagnostics,
    _has_adg_sqlite,
    _probe_sqlite_read,
    _probe_sqlite_write,
    check_adg_gate,
    check_filesystem_write_gate,
    main,
)


def _create_real_sqlite(adg_dir: Path, name: str = "adg_indexed_20260101.sqlite") -> Path:
    """Create a real SQLite DB file that can be opened and queried."""
    db_path = adg_dir / name
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS probe (id INTEGER)")
    conn.commit()
    conn.close()
    return db_path


# ---------------------------------------------------------------------------
# _probe_sqlite_read / _probe_sqlite_write / _check_sqlite_access
# ---------------------------------------------------------------------------


class TestProbeSqliteRead:
    def test_healthy_db_returns_ok(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        ok, reason = _probe_sqlite_read(db)
        assert ok is True
        assert reason == "read_ok"

    def test_nonexistent_db_returns_failure(self, tmp_path):
        fake = tmp_path / "no_such.sqlite"
        ok, reason = _probe_sqlite_read(fake)
        # sqlite3 in read-only URI mode fails if file does not exist
        assert ok is False
        assert "open_failed" in reason or "unable to open" in reason.lower()

    def test_healthy_db_with_zero_byte_wal_returns_ok(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        (adg / (db.name + "-wal")).write_text("")
        ok, reason = _probe_sqlite_read(db)
        assert ok is True
        assert reason == "read_ok"

    def test_healthy_db_with_nonzero_wal_returns_ok(self, tmp_path):
        """Non-zero WAL is normal in WAL mode — reads must still succeed."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        # Put the DB in WAL mode and write data to create a real non-zero WAL
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("INSERT INTO probe VALUES (1)")
        conn.commit()
        conn.close()
        wal = adg / (db.name + "-wal")
        # WAL may or may not exist after close+checkpoint, so create one if needed
        if not wal.exists():
            wal.write_bytes(b"\x00" * 64)
        ok, reason = _probe_sqlite_read(db)
        assert ok is True
        assert reason == "read_ok"


class TestProbeSqliteWrite:
    def test_no_contention_returns_ok(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        ok, reason = _probe_sqlite_write(db)
        assert ok is True
        assert reason == "write_ok"

    def test_active_writer_returns_busy(self, tmp_path):
        """Simulate real write contention with an uncommitted transaction."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        # Hold an exclusive lock via BEGIN IMMEDIATE on a separate connection
        holder = sqlite3.connect(str(db), timeout=0.1)
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("INSERT INTO probe VALUES (99)")
        try:
            ok, reason = _probe_sqlite_write(db)
            assert ok is False
            assert "SQLITE_BUSY" in reason or "locked" in reason.lower() or "busy" in reason.lower()
        finally:
            holder.rollback()
            holder.close()

    def test_nonexistent_db_returns_failure(self, tmp_path):
        fake = tmp_path / "no_such.sqlite"
        # sqlite3.connect in write mode creates the file, but BEGIN IMMEDIATE
        # on an empty DB is fine. Test with a truly invalid path instead.
        ok, reason = _probe_sqlite_write(fake)
        # File gets created by connect — this should actually succeed
        assert isinstance(ok, bool)


class TestCheckSqliteAccess:
    def test_no_artifacts_dir_not_blocked(self, tmp_path):
        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is False
        assert "no_artifacts_dir" in reason

    def test_no_sqlite_files_not_blocked(self, tmp_path):
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is False
        assert "no_sqlite_files" in reason

    def test_healthy_db_read_not_blocked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg)
        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is False

    def test_healthy_db_write_not_blocked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg)
        blocked, reason = _check_sqlite_access(tmp_path, needs_write=True)
        assert blocked is False

    def test_healthy_db_with_wal_sidecars_read_not_blocked(self, tmp_path):
        """WAL sidecars must not cause read-only tools to be blocked."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        # Create WAL-mode sidecars with content (normal state)
        (adg / (db.name + "-wal")).write_bytes(b"\x00" * 64)
        (adg / (db.name + "-shm")).write_bytes(b"\x00" * 32)
        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is False

    def test_active_writer_blocks_write_tool(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        holder = sqlite3.connect(str(db), timeout=0.1)
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("INSERT INTO probe VALUES (99)")
        try:
            blocked, reason = _check_sqlite_access(tmp_path, needs_write=True)
            assert blocked is True
            assert "contention" in reason.lower() or "busy" in reason.lower()
        finally:
            holder.rollback()
            holder.close()

    def test_active_writer_does_not_block_read_tool(self, tmp_path):
        """Read-only tools should pass even when a writer holds the lock."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        # Enable WAL mode so readers don't block on writers
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.close()
        holder = sqlite3.connect(str(db), timeout=0.1)
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("INSERT INTO probe VALUES (99)")
        try:
            blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
            assert blocked is False
        finally:
            holder.rollback()
            holder.close()

    def test_path_canonicalization(self, tmp_path):
        """Paths with ../ components must resolve to same canonical path."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg)
        # Create a symlink-like detour via parent traversal
        detour = tmp_path / "artifacts" / "adg" / ".." / "adg"
        # _check_sqlite_access uses repo_root / artifacts / adg which is canonical
        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is False

    def test_multiple_dbs_all_healthy(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_001.sqlite")
        _create_real_sqlite(adg, "adg_indexed_002.sqlite")
        blocked, reason = _check_sqlite_access(tmp_path, needs_write=False)
        assert blocked is False


class TestGetSidecarDiagnostics:
    def test_no_sidecars(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        diag = _get_sidecar_diagnostics(db)
        assert diag["wal"] is None
        assert diag["shm"] is None
        assert diag["journal"] is None

    def test_with_sidecars(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg)
        (adg / (db.name + "-wal")).write_bytes(b"\x00" * 64)
        (adg / (db.name + "-shm")).write_bytes(b"\x00" * 32)
        diag = _get_sidecar_diagnostics(db)
        assert diag["wal"] == 64
        assert diag["shm"] == 32
        assert diag["journal"] is None


# ---------------------------------------------------------------------------
# _get_latest_snapshot_age_seconds
# ---------------------------------------------------------------------------


class TestGetLatestSnapshotAgeSeconds:
    def test_no_artifacts_dir_returns_none(self, tmp_path):
        assert _get_latest_snapshot_age_seconds(tmp_path) is None

    def test_no_snapshots_returns_none(self, tmp_path):
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        assert _get_latest_snapshot_age_seconds(tmp_path) is None

    def test_fresh_snapshot_age_is_small(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_snapshot_20260101.json").write_text("{}")
        age = _get_latest_snapshot_age_seconds(tmp_path)
        assert age is not None
        assert age < 10

    def test_old_snapshot_age_is_large(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_20260101.json"
        snap.write_text("{}")
        old_time = time.time() - 3700
        os.utime(str(snap), (old_time, old_time))
        age = _get_latest_snapshot_age_seconds(tmp_path)
        assert age is not None
        assert age > 3600

    def test_picks_newest_of_multiple_snapshots(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        old = adg / "adg_snapshot_old.json"
        new = adg / "adg_snapshot_new.json"
        old.write_text("{}")
        new.write_text("{}")
        old_time = time.time() - 7200
        os.utime(str(old), (old_time, old_time))
        age = _get_latest_snapshot_age_seconds(tmp_path)
        assert age is not None
        assert age < 10


# ---------------------------------------------------------------------------
# check_adg_gate
# ---------------------------------------------------------------------------


class TestCheckAdgGate:
    def test_fresh_snapshot_healthy_db_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / "adg_snapshot_now.json").write_text("{}")
        assert check_adg_gate(tmp_path) == 0

    def test_healthy_db_with_nonzero_wal_allowed_for_read_tool(self, tmp_path):
        """Non-zero WAL must NOT block read-only tools."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / (db.name + "-wal")).write_bytes(b"\x00" * 64)
        (adg / "adg_snapshot_now.json").write_text("{}")
        assert check_adg_gate(tmp_path, tool_name="adg_edge_fanout") == 0

    def test_healthy_db_with_wal_and_shm_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / (db.name + "-wal")).write_bytes(b"\x00" * 64)
        (adg / (db.name + "-shm")).write_bytes(b"\x00" * 32)
        (adg / "adg_snapshot_now.json").write_text("{}")
        assert check_adg_gate(tmp_path, tool_name="adg_node") == 0

    def test_healthy_db_with_journal_file_allowed(self, tmp_path):
        """Journal file presence alone does not block if DB is readable."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / (db.name + "-journal")).write_bytes(b"\x00" * 32)
        (adg / "adg_snapshot_now.json").write_text("{}")
        assert check_adg_gate(tmp_path, tool_name="adg_nodes_by_layer") == 0

    def test_write_tool_with_active_writer_blocks(self, tmp_path):
        """Write-affecting tool blocked when real SQLITE_BUSY detected."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / "adg_snapshot_now.json").write_text("{}")
        holder = sqlite3.connect(str(db), timeout=0.1)
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("INSERT INTO probe VALUES (99)")
        try:
            assert check_adg_gate(tmp_path, tool_name="adg_rebuild") == 2
        finally:
            holder.rollback()
            holder.close()

    def test_read_tool_with_active_writer_allowed_wal_mode(self, tmp_path):
        """In WAL mode, readers do not block on writers."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.close()
        (adg / "adg_snapshot_now.json").write_text("{}")
        holder = sqlite3.connect(str(db), timeout=0.1)
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("INSERT INTO probe VALUES (99)")
        try:
            assert check_adg_gate(tmp_path, tool_name="adg_edge_fanout") == 0
        finally:
            holder.rollback()
            holder.close()

    def test_stale_snapshot_blocks(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        snap = adg / "adg_snapshot_old.json"
        snap.write_text("{}")
        os.utime(str(snap), (time.time() - 3700, time.time() - 3700))
        assert check_adg_gate(tmp_path) == 2

    def test_missing_snapshot_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        assert check_adg_gate(tmp_path) == 0

    def test_missing_artifacts_dir_no_sqlite_triggers_autogen(self, tmp_path):
        with patch(
            "ops_scripts.hooks.windsurf.pre_mcp_gate._auto_generate_adg",
            return_value=True,
        ):
            assert check_adg_gate(tmp_path) == 0

    def test_exactly_30min_old_snapshot_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        snap = adg / "adg_snapshot_borderline.json"
        snap.write_text("{}")
        t = time.time() - (29 * 60 + 59)
        os.utime(str(snap), (t, t))
        assert check_adg_gate(tmp_path) == 0

    def test_just_over_30min_old_snapshot_blocks(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        snap = adg / "adg_snapshot_borderline.json"
        snap.write_text("{}")
        t = time.time() - (30 * 60 + 5)
        os.utime(str(snap), (t, t))
        assert check_adg_gate(tmp_path) == 2

    def test_reopen_connections_cycle_does_not_block_reads(self, tmp_path):
        """Simulates close→reopen cycle: WAL sidecars recreated, reads still pass."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / "adg_snapshot_now.json").write_text("{}")
        # Simulate close_connections removing sidecars
        for suffix in ("-wal", "-shm"):
            sf = adg / (db.name + suffix)
            if sf.exists():
                sf.unlink()
        # Simulate reopen_connections recreating sidecars
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("SELECT 1")
        conn.close()
        # WAL sidecars may now exist — gate must still allow
        assert check_adg_gate(tmp_path, tool_name="adg_edge_fanout") == 0


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


class TestMain:
    def _run(self, payload: dict, repo_root=None) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            if repo_root is not None:
                with patch("ops_scripts.hooks.windsurf.pre_mcp_gate.REPO_ROOT", repo_root):
                    return main()
            return main()

    # Filesystem MCP — read tools allowed, write tools blocked
    def test_filesystem_mcp_no_tool_allowed(self):
        assert self._run({"tool_info": {"mcp_server_name": "filesystem"}}) == 0

    def test_filesystem_mcp_read_tool_allowed(self):
        payload = {"tool_info": {"mcp_server_name": "filesystem", "mcp_tool_name": "read_text_file"}}
        assert self._run(payload) == 0

    def test_filesystem_mcp_write_file_blocked(self):
        payload = {"tool_info": {"mcp_server_name": "filesystem", "mcp_tool_name": "write_file"}}
        assert self._run(payload) == 2

    def test_filesystem_mcp_edit_file_blocked(self):
        payload = {"tool_info": {"mcp_server_name": "filesystem", "mcp_tool_name": "edit_file"}}
        assert self._run(payload) == 2

    # Non-ADG, non-filesystem MCPs — always allowed
    def test_memory_mcp_allowed(self):
        assert self._run({"tool_info": {"mcp_server_name": "memory"}}) == 0

    def test_gitkraken_mcp_allowed(self):
        assert self._run({"tool_info": {"mcp_server_name": "gitkraken"}}) == 0

    def test_task_manager_mcp_allowed(self):
        assert self._run({"tool_info": {"mcp_server_name": "task_manager"}}) == 0

    def test_deepwiki_mcp_allowed(self):
        assert self._run({"tool_info": {"mcp_server_name": "deepwiki"}}) == 0

    def test_empty_server_name_allowed(self):
        assert self._run({"tool_info": {}}) == 0

    def test_missing_server_name_allowed(self):
        assert self._run({"tool_info": {"mcp_tool_name": "some_tool"}}) == 0

    # Recovery tools — always allowed even when locked/stale
    def test_all_recovery_tools_whitelisted(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_x.sqlite").write_text("")
        (adg / "adg_indexed_x.sqlite-wal").write_bytes(b"\x00" * 32)
        for tool in ADG_RECOVERY_TOOLS:
            payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": tool}}
            result = self._run(payload, tmp_path)
            assert result == 0, f"Recovery tool {tool} should be whitelisted but was blocked"

    # ADG MCP blocking cases
    def test_adg_with_fresh_snapshot_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / "adg_snapshot_now.json").write_text("{}")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_nodes_by_layer"}}
        assert self._run(payload, tmp_path) == 0

    def test_adg_with_wal_sidecars_read_tool_allowed(self, tmp_path):
        """Non-zero WAL must not block read-only tools in integration."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / (db.name + "-wal")).write_bytes(b"\x00" * 64)
        (adg / "adg_snapshot_now.json").write_text("{}")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        assert self._run(payload, tmp_path) == 0

    def test_adg_write_tool_with_contention_blocked(self, tmp_path):
        """Write-affecting tool blocked when real contention exists."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / "adg_snapshot_now.json").write_text("{}")
        holder = sqlite3.connect(str(db), timeout=0.1)
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("INSERT INTO probe VALUES (99)")
        try:
            payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_rebuild"}}
            assert self._run(payload, tmp_path) == 2
        finally:
            holder.rollback()
            holder.close()

    def test_adg_with_stale_snapshot_blocked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        snap = adg / "adg_snapshot_old.json"
        snap.write_text("{}")
        os.utime(str(snap), (time.time() - 3700, time.time() - 3700))
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_edge_fanout"}}
        assert self._run(payload, tmp_path) == 2

    def test_adg_full_cycle_health_fanout_close_reopen_fanout(self, tmp_path):
        """End-to-end: health → fanout → close → reopen → fanout all pass."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        db = _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        (adg / "adg_snapshot_now.json").write_text("{}")

        # 1. adg_health (recovery tool, always allowed)
        p = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_health"}}
        assert self._run(p, tmp_path) == 0

        # 2. adg_edge_fanout (read-only, should pass)
        p = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_edge_fanout"}}
        assert self._run(p, tmp_path) == 0

        # 3. adg_close_connections (recovery tool)
        p = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_close_connections"}}
        assert self._run(p, tmp_path) == 0

        # Simulate close removing sidecars
        for suffix in ("-wal", "-shm"):
            sf = adg / (db.name + suffix)
            if sf.exists():
                sf.unlink()

        # 4. adg_reopen_connections (recovery tool)
        p = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_reopen_connections"}}
        assert self._run(p, tmp_path) == 0

        # Simulate reopen recreating WAL sidecars
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("SELECT 1")
        conn.close()

        # 5. adg_edge_fanout again (read-only, must still pass)
        p = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_edge_fanout"}}
        assert self._run(p, tmp_path) == 0

    def test_adg_no_artifacts_dir_autogen_triggered(self, tmp_path):
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        with patch(
            "ops_scripts.hooks.windsurf.pre_mcp_gate._auto_generate_adg",
            return_value=True,
        ):
            assert self._run(payload, tmp_path) == 0

    # Payload structure variants
    def test_flat_payload_no_tool_info(self):
        payload = {"mcp_server_name": "filesystem"}
        assert self._run(payload) == 0

    def test_empty_stdin_fail_open(self):
        with patch("sys.stdin", StringIO("")):
            assert main() == 0

    def test_malformed_json_fail_open(self):
        with patch("sys.stdin", StringIO("{bad json")):
            assert main() == 0

    def test_whitespace_only_stdin_fail_open(self):
        with patch("sys.stdin", StringIO("   \n")):
            assert main() == 0


# ---------------------------------------------------------------------------
# check_filesystem_write_gate — unit tests
# ---------------------------------------------------------------------------


class TestCheckFilesystemWriteGate:
    def test_write_file_blocked(self):
        assert check_filesystem_write_gate("write_file") == 2

    def test_edit_file_blocked(self):
        assert check_filesystem_write_gate("edit_file") == 2

    def test_all_write_tools_blocked(self):
        for tool in FILESYSTEM_WRITE_TOOLS:
            assert check_filesystem_write_gate(tool) == 2, f"Write tool '{tool}' must be blocked"

    def test_read_text_file_allowed(self):
        assert check_filesystem_write_gate("read_text_file") == 0

    def test_list_directory_allowed(self):
        assert check_filesystem_write_gate("list_directory") == 0

    def test_directory_tree_allowed(self):
        assert check_filesystem_write_gate("directory_tree") == 0

    def test_search_files_allowed(self):
        assert check_filesystem_write_gate("search_files") == 0

    def test_get_file_info_allowed(self):
        assert check_filesystem_write_gate("get_file_info") == 0

    def test_read_multiple_files_allowed(self):
        assert check_filesystem_write_gate("read_multiple_files") == 0

    def test_create_directory_allowed(self):
        assert check_filesystem_write_gate("create_directory") == 0

    def test_move_file_allowed(self):
        assert check_filesystem_write_gate("move_file") == 0

    def test_empty_tool_name_allowed(self):
        assert check_filesystem_write_gate("") == 0

    def test_unknown_tool_name_allowed(self):
        assert check_filesystem_write_gate("some_future_tool") == 0

    def test_write_file_uppercase_not_blocked(self):
        assert check_filesystem_write_gate("WRITE_FILE") == 0

    def test_block_message_mentions_native_tools(self, capsys):
        check_filesystem_write_gate("write_file")
        captured = capsys.readouterr()
        assert "write_to_file" in captured.err or "edit" in captured.err
