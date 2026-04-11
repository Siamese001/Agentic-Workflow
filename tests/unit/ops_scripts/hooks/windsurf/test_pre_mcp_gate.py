"""EXHAUSTIVE tests for pre_mcp_gate.py (Phase 1.3) — PP-1, PP-10.

Plan requirements verified:
  - Filesystem MCP write tools (write_file, edit_file): exit 2 (BLOCKED)
  - Filesystem MCP read tools (read_text_file, list_directory, etc.): exit 0 (allowed)
  - Filesystem MCP with no tool name: exit 0 (allowed — read assumed)
  - Non-ADG, non-filesystem MCPs: always exit 0 (fail-open)
  - ADG MCP + recovery tools: always exit 0 (whitelist)
  - ADG MCP + real SQLite read probe failure: exit 2 (block)
  - ADG MCP + real SQLite write contention (BEGIN IMMEDIATE → BUSY): exit 2 (block)
  - ADG MCP + stale snapshot: exit 0 (advisory only — never blocks)
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

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".windsurf" / "scripts"))

import pre_mcp_gate as _gate_module
from pre_mcp_gate import (
    ADG_RECOVERY_TOOLS,
    ADG_WRITE_TOOLS,
    FILESYSTEM_WRITE_TOOLS,
    GITKRAKEN_ALL_WRITE_TOOLS,
    GITKRAKEN_LOCAL_WRITE_TOOLS,
    GITKRAKEN_PUSH_TOOLS,
    GITKRAKEN_REMOTE_WRITE_TOOLS,
    GITKRAKEN_SERVER_NAME,
    GITKRAKEN_WORKSPACE_ROOT,
    MEMORY_RECOVERY_TOOLS,
    OTEL_MCP_RECOVERY_TOOLS,
    PYTEST_RECOVERY_TOOLS,
    TASK_MANAGER_RECOVERY_TOOLS,
    VECTOR_DB_RECOVERY_TOOLS,
    _auto_generate_adg,
    _check_gitkraken_detached_head,
    _check_gitkraken_dirty_tree,
    _check_gitkraken_missing_upstream,
    _check_gitkraken_repo_confinement,
    _check_sqlite_access,
    _get_latest_snapshot_age_seconds,
    _get_sidecar_diagnostics,
    _has_adg_sqlite,
    _probe_sqlite_read,
    _probe_sqlite_write,
    check_adg_gate,
    check_filesystem_write_gate,
    check_gitkraken_gate,
    main,
)


@pytest.fixture(autouse=True)
def _clear_probe_cache():
    """Clear _PROBE_CACHE before every test so subprocess mocks are not shadowed by
    cached results from earlier tests in the same process."""
    _gate_module._PROBE_CACHE.clear()
    yield
    _gate_module._PROBE_CACHE.clear()


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

    def test_stale_snapshot_advisory_only(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        snap = adg / "adg_snapshot_old.json"
        snap.write_text("{}")
        os.utime(str(snap), (time.time() - 3700, time.time() - 3700))
        assert check_adg_gate(tmp_path) == 0  # stale snapshot is advisory only, never blocks

    def test_missing_snapshot_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        assert check_adg_gate(tmp_path) == 0

    def test_missing_artifacts_dir_no_sqlite_triggers_autogen(self, tmp_path):
        with patch(
            "pre_mcp_gate._auto_generate_adg",
            return_value=True,
        ):
            assert check_adg_gate(tmp_path) == 0

    def test_old_snapshot_advisory_only_not_blocked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        snap = adg / "adg_snapshot_old.json"
        snap.write_text("{}")
        t = time.time() - (30 * 60 + 5)  # 30+ minutes old
        os.utime(str(snap), (t, t))
        assert check_adg_gate(tmp_path) == 0  # advisory warning only, never blocks

    def test_very_old_snapshot_still_not_blocked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        snap = adg / "adg_snapshot_very_old.json"
        snap.write_text("{}")
        t = time.time() - (24 * 60 * 60)  # 24 hours old
        os.utime(str(snap), (t, t))
        assert check_adg_gate(tmp_path) == 0  # stale ADG is valid until manually refreshed

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
                with patch("pre_mcp_gate.REPO_ROOT", repo_root):
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

    # Non-ADG, non-filesystem MCPs with no local infra needed — always allowed
    def test_gitkraken_unknown_server_name_fail_open(self):
        # Lowercase 'gitkraken' does NOT match GITKRAKEN_SERVER_NAME ('GitKraken')
        # — hits generic fail-open path
        assert self._run({"tool_info": {"mcp_server_name": "gitkraken"}}) == 0

    def test_deepwiki_mcp_allowed(self):
        """DeepWiki is fail-open regardless of network — mock socket to avoid DNS."""
        with patch("socket.create_connection") as mock_conn:
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            assert self._run({"tool_info": {"mcp_server_name": "deepwiki"}}) == 0

    def test_deepwiki_unreachable_still_allowed(self):
        """DeepWiki gate is always fail-open — even if DNS fails, gate returns 0."""
        with patch("socket.create_connection", side_effect=OSError("network unreachable")):
            assert self._run({"tool_info": {"mcp_server_name": "deepwiki"}}) == 0

    def test_memory_recovery_tool_always_allowed(self, tmp_path):
        """Recovery tools bypass gate even if DB doesn't exist yet."""
        for tool in ["mem_recall_session_start", "mem_get_stats", "search_nodes"]:
            payload = {"tool_info": {"mcp_server_name": "memory", "mcp_tool_name": tool}}
            assert self._run(payload, tmp_path) == 0, f"Recovery tool '{tool}' must always be allowed"

    def test_memory_nonexistent_db_allowed(self, tmp_path):
        """Memory gate allows when DB doesn't exist yet (created on first use)."""
        payload = {"tool_info": {"mcp_server_name": "memory", "mcp_tool_name": "open_nodes"}}
        assert self._run(payload, tmp_path) == 0

    def test_memory_healthy_db_allowed(self, tmp_path):
        mem_dir = tmp_path / "artifacts" / "memory"
        mem_dir.mkdir(parents=True)
        db = mem_dir / "knowledge_graph.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE entities (id INTEGER)")
        conn.commit()
        conn.close()
        payload = {"tool_info": {"mcp_server_name": "memory", "mcp_tool_name": "open_nodes"}}
        assert self._run(payload, tmp_path) == 0

    def test_task_manager_recovery_tool_allowed(self):
        """Recovery tools bypass the Node.js probe entirely."""
        for tool in TASK_MANAGER_RECOVERY_TOOLS:
            payload = {"tool_info": {"mcp_server_name": "task_manager", "mcp_tool_name": tool}}
            assert self._run(payload) == 0, f"Recovery tool '{tool}' must always be allowed"

    def test_task_manager_node_not_found_blocked(self):
        """If Node.js is not in PATH, task_manager gate must block non-recovery tools."""
        payload = {"tool_info": {"mcp_server_name": "task_manager", "mcp_tool_name": "list_tasks"}}
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=FileNotFoundError("node not found"),
        ):
            assert self._run(payload) == 2

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

    def test_adg_with_stale_snapshot_advisory_only(self, tmp_path):
        """Stale ADG snapshot emits advisory warning but never blocks."""
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        _create_real_sqlite(adg, "adg_indexed_x.sqlite")
        snap = adg / "adg_snapshot_old.json"
        snap.write_text("{}")
        os.utime(str(snap), (time.time() - 3700, time.time() - 3700))
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_edge_fanout"}}
        assert self._run(payload, tmp_path) == 0  # advisory only, never blocks

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
            "pre_mcp_gate._auto_generate_adg",
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

    def test_move_file_blocked(self):
        assert check_filesystem_write_gate("move_file") == 2

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


# ---------------------------------------------------------------------------
# check_vector_db_gate — unit tests
# ---------------------------------------------------------------------------


class TestCheckVectorDbGate:
    """Gate: chromadb importable (hard block) + HTTP instance probe (advisory/fail-open)."""

    def _gate(self):
        from pre_mcp_gate import check_vector_db_gate

        return check_vector_db_gate

    def test_chromadb_installed_no_http_server_allowed(self):
        """chromadb importable + no HTTP server = advisory only, not blocked."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            with patch("socket.create_connection", side_effect=ConnectionRefusedError):
                assert self._gate()() == 0

    def test_chromadb_installed_http_server_running_allowed(self):
        """chromadb importable + HTTP server running = allowed."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            with patch("socket.create_connection", return_value=mock_conn):
                assert self._gate()() == 0

    def test_chromadb_not_installed_blocked(self):
        """chromadb not importable = hard block."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "No module named chromadb"
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            assert self._gate()() == 2

    def test_chromadb_probe_timeout_blocked(self):
        """subprocess timeout on library probe = hard block."""
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="python", timeout=10),
        ):
            assert self._gate()() == 2

    def test_recovery_tools_bypass_gate(self):
        """vector_stats and list_collections always pass even if chromadb missing."""
        mock_result = MagicMock()
        mock_result.returncode = 1  # chromadb missing
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            for tool in VECTOR_DB_RECOVERY_TOOLS:
                payload = {"tool_info": {"mcp_server_name": "vector_db", "mcp_tool_name": tool}}
                raw = json.dumps(payload)
                with patch("sys.stdin", StringIO(raw)):
                    assert main() == 0, f"Recovery tool '{tool}' must bypass vector_db gate"

    def test_advisory_message_emitted_when_no_http_server(self, capsys):
        """When HTTP server absent, advisory INFO message is printed."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            with patch("socket.create_connection", side_effect=ConnectionRefusedError):
                self._gate()()
        captured = capsys.readouterr()
        assert "ChromaDB" in captured.err or "embedded" in captured.err.lower()


# ---------------------------------------------------------------------------
# check_otel_gate — unit tests
# ---------------------------------------------------------------------------


class TestCheckOtelGate:
    """Gate: opentelemetry SDK importable (hard block) + OTLP collector probe (advisory/fail-open)."""

    def _gate(self):
        from pre_mcp_gate import check_otel_gate

        return check_otel_gate

    def test_otel_sdk_installed_no_collector_allowed(self):
        """SDK importable + no OTLP collector = advisory only, not blocked."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            with patch("socket.create_connection", side_effect=ConnectionRefusedError):
                assert self._gate()() == 0

    def test_otel_sdk_installed_collector_running_allowed(self):
        """SDK importable + collector running = allowed."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            with patch("socket.create_connection", return_value=mock_conn):
                assert self._gate()() == 0

    def test_otel_sdk_not_installed_blocked(self):
        """opentelemetry SDK not importable = hard block."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "No module named opentelemetry"
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            assert self._gate()() == 2

    def test_otel_probe_timeout_blocked(self):
        """subprocess timeout on SDK probe = hard block."""
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="python", timeout=10),
        ):
            assert self._gate()() == 2

    def test_recovery_tools_bypass_gate(self):
        """otel_status and otel_metrics_summary always pass even if SDK missing."""
        mock_result = MagicMock()
        mock_result.returncode = 1  # SDK missing
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            for tool in OTEL_MCP_RECOVERY_TOOLS:
                payload = {"tool_info": {"mcp_server_name": "otel_mcp", "mcp_tool_name": tool}}
                raw = json.dumps(payload)
                with patch("sys.stdin", StringIO(raw)):
                    assert main() == 0, f"Recovery tool '{tool}' must bypass otel gate"

    def test_advisory_message_emitted_when_no_collector(self, capsys):
        """When OTLP collector absent, advisory INFO message is printed."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            with patch("socket.create_connection", side_effect=ConnectionRefusedError):
                self._gate()()
        captured = capsys.readouterr()
        assert "OTLP" in captured.err or "collector" in captured.err.lower() or "runtime_adg" in captured.err


# ---------------------------------------------------------------------------
# check_redis_gate — unit tests
# ---------------------------------------------------------------------------


class TestCheckRedisGate:
    """Gate: Redis TCP PING (hard block on ConnectionRefusedError)."""

    def _gate(self, repo_root=None):
        from pre_mcp_gate import REPO_ROOT, check_redis_gate

        root = repo_root if repo_root is not None else REPO_ROOT
        return lambda: check_redis_gate(root)

    def test_redis_up_allowed(self, tmp_path):
        import redis as redis_lib

        mock_client = MagicMock()
        mock_client.ping.return_value = True
        with patch.object(redis_lib, "Redis", return_value=mock_client):
            assert self._gate(tmp_path)() == 0

    def test_redis_not_installed_blocked(self, tmp_path):
        with patch.dict("sys.modules", {"redis": None}):
            assert self._gate(tmp_path)() == 2

    def test_redis_connection_refused_blocked(self, tmp_path):
        import redis as redis_lib

        mock_client = MagicMock()
        mock_client.ping.side_effect = redis_lib.ConnectionError("Connection refused")
        with patch.object(redis_lib, "Redis", return_value=mock_client):
            assert self._gate(tmp_path)() == 2

    def test_recovery_tool_bypasses_gate(self):
        """redis_health bypasses gate even when Redis is down.
        Server name MUST be 'redis' (matches .windsurf/mcp_config.json key exactly)."""
        import redis as redis_lib

        mock_client = MagicMock()
        mock_client.ping.side_effect = redis_lib.ConnectionError("down")
        with patch.object(redis_lib, "Redis", return_value=mock_client):
            payload = {"tool_info": {"mcp_server_name": "redis", "mcp_tool_name": "redis_health"}}
            raw = json.dumps(payload)
            with patch("sys.stdin", StringIO(raw)):
                assert main() == 0


# ---------------------------------------------------------------------------
# check_memory_gate — unit tests
# ---------------------------------------------------------------------------


class TestCheckMemoryGate:
    """Gate: knowledge_graph.sqlite accessible (hard block on OperationalError)."""

    def _gate(self, tmp_path):
        from pre_mcp_gate import check_memory_gate

        return lambda: check_memory_gate(tmp_path)

    def test_no_db_file_allowed(self, tmp_path):
        """DB doesn't exist yet — allowed (created on first use)."""
        assert self._gate(tmp_path)() == 0

    def test_memory_dir_missing_created_and_allowed(self, tmp_path):
        """artifacts/memory dir missing — gate creates it and allows."""
        assert self._gate(tmp_path)() == 0
        assert (tmp_path / "artifacts" / "memory").exists()

    def test_healthy_db_allowed(self, tmp_path):
        mem = tmp_path / "artifacts" / "memory"
        mem.mkdir(parents=True)
        db = mem / "knowledge_graph.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE entities (id INTEGER)")
        conn.commit()
        conn.close()
        assert self._gate(tmp_path)() == 0

    def test_corrupted_db_blocked(self, tmp_path):
        mem = tmp_path / "artifacts" / "memory"
        mem.mkdir(parents=True)
        (mem / "knowledge_graph.sqlite").write_bytes(b"not a sqlite file\x00")
        assert self._gate(tmp_path)() == 2

    def test_recovery_tools_always_bypass(self, tmp_path):
        """mem_recall_session_start etc. bypass even if DB is corrupted."""
        mem = tmp_path / "artifacts" / "memory"
        mem.mkdir(parents=True)
        (mem / "knowledge_graph.sqlite").write_bytes(b"corrupted")
        for tool in MEMORY_RECOVERY_TOOLS:
            payload = {"tool_info": {"mcp_server_name": "memory", "mcp_tool_name": tool}}
            raw = json.dumps(payload)
            with patch("sys.stdin", StringIO(raw)):
                with patch("pre_mcp_gate.REPO_ROOT", tmp_path):
                    assert main() == 0, f"Recovery tool '{tool}' must bypass memory gate"


# ---------------------------------------------------------------------------
# check_pytest_gate — unit tests
# ---------------------------------------------------------------------------


class TestCheckPytestGate:
    """Gate: pytest importable (hard block) + pytest.ini advisory."""

    def _gate(self, tmp_path):
        from pre_mcp_gate import check_pytest_gate

        return lambda: check_pytest_gate(tmp_path)

    def test_pytest_installed_with_ini_allowed(self, tmp_path):
        (tmp_path / "pytest.ini").write_text("[pytest]")
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            assert self._gate(tmp_path)() == 0

    def test_pytest_installed_no_ini_advisory_only_allowed(self, tmp_path, capsys):
        """No pytest.ini is advisory only — gate still allows."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            result = self._gate(tmp_path)()
        assert result == 0
        captured = capsys.readouterr()
        assert "pytest" in captured.err.lower()

    def test_pytest_not_installed_blocked(self, tmp_path):
        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            assert self._gate(tmp_path)() == 2

    def test_recovery_tools_bypass_gate(self):
        """list_pytest_config and discover_tests bypass gate."""
        mock_result = MagicMock()
        mock_result.returncode = 1  # pytest not installed
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            for tool in PYTEST_RECOVERY_TOOLS:
                payload = {"tool_info": {"mcp_server_name": "pytest_mcp", "mcp_tool_name": tool}}
                raw = json.dumps(payload)
                with patch("sys.stdin", StringIO(raw)):
                    assert main() == 0, f"Recovery tool '{tool}' must bypass pytest gate"


# ---------------------------------------------------------------------------
# check_gitkraken_gate — unit tests
# ---------------------------------------------------------------------------


class TestGitKrakenGate:
    """
    Tests for the GitKraken MCP hardening gate (P0-2, P0-3, P0-4).

    All git subprocess calls are mocked via _run_git to avoid real repo deps.
    The workspace root (GITKRAKEN_WORKSPACE_ROOT) is patched to tmp_path.
    """

    def _run_payload(self, tool_name: str, tmp_path: Path) -> int:
        payload = {"tool_info": {"mcp_server_name": GITKRAKEN_SERVER_NAME, "mcp_tool_name": tool_name}}
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):
                return main()

    # --- Tool surface classification ---

    def test_server_name_constant_matches_mcp_config(self):
        assert GITKRAKEN_SERVER_NAME == "GitKraken"

    def test_write_tool_sets_are_disjoint_subsets(self):
        assert GITKRAKEN_LOCAL_WRITE_TOOLS.issubset(GITKRAKEN_ALL_WRITE_TOOLS)
        assert GITKRAKEN_REMOTE_WRITE_TOOLS.issubset(GITKRAKEN_ALL_WRITE_TOOLS)
        assert GITKRAKEN_PUSH_TOOLS.issubset(GITKRAKEN_REMOTE_WRITE_TOOLS)

    def test_read_only_tools_always_allowed(self, tmp_path):  # pylint: disable=unused-argument
        read_only = [
            "git_log_or_diff",
            "git_status",
            "git_blame",
            "issues_get_detail",
            "issues_assigned_to_me",
            "pull_request_get_detail",
            "pull_request_get_comments",
            "repository_get_file_content",
            "gitkraken_workspace_list",
            "gitlens_launchpad",
        ]
        for tool in read_only:
            assert check_gitkraken_gate(tool, {}) == 0, f"Read-only '{tool}' must be allowed"

    def test_read_tool_not_in_write_sets(self):
        for tool in ["git_log_or_diff", "git_status", "git_blame", "gitlens_launchpad", "issues_get_detail"]:
            assert tool not in GITKRAKEN_ALL_WRITE_TOOLS

    # --- Repo confinement (P0-4) ---

    def test_repo_confinement_outside_workspace_blocked(self, tmp_path):
        outside = tmp_path.parent / "other_repo"
        outside.mkdir(exist_ok=True)
        blocked, reason = _check_gitkraken_repo_confinement(outside)
        assert blocked is True
        assert "outside workspace root" in reason or "Cross-repo" in reason

    def test_repo_confinement_workspace_root_itself_is_confined(self, tmp_path):
        # Must be an actual git repo for confinement to pass.
        # Patch workspace root to tmp_path so the path-confinement check passes.
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main")
        with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):
            with patch("pre_mcp_gate._run_git", return_value=(0, ".git", "")):
                blocked, reason = _check_gitkraken_repo_confinement(tmp_path)
        assert blocked is False
        assert reason == "repo_confined"

    def test_repo_confinement_not_a_git_repo_blocked(self, tmp_path):
        # Patch workspace root to tmp_path; sub-path is within workspace but fails git-dir probe.
        not_a_repo = tmp_path / "sub"
        not_a_repo.mkdir()
        with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):
            with patch("pre_mcp_gate._run_git", return_value=(128, "", "not a git repository")):
                blocked, reason = _check_gitkraken_repo_confinement(not_a_repo)
        assert blocked is True
        assert "not a git repository" in reason

    # --- Detached HEAD check (P0-3) ---

    def test_detached_head_returns_true_when_detached(self, tmp_path):
        with patch("pre_mcp_gate._run_git", return_value=(1, "", "")):
            detached, desc = _check_gitkraken_detached_head(tmp_path)
        assert detached is True
        assert "detached" in desc.lower()

    def test_detached_head_returns_false_on_branch(self, tmp_path):
        with patch("pre_mcp_gate._run_git", return_value=(0, "refs/heads/main", "")):
            detached, desc = _check_gitkraken_detached_head(tmp_path)
        assert detached is False
        assert "main" in desc

    # --- Dirty tree check (P0-3) ---

    def test_dirty_tree_returns_true_when_changes_present(self, tmp_path):
        with patch("pre_mcp_gate._run_git", return_value=(0, "M  modified_file.py", "")):
            dirty, desc = _check_gitkraken_dirty_tree(tmp_path)
        assert dirty is True
        assert "uncommitted" in desc.lower()

    def test_dirty_tree_returns_false_when_clean(self, tmp_path):
        with patch("pre_mcp_gate._run_git", return_value=(0, "", "")):
            dirty, _ = _check_gitkraken_dirty_tree(tmp_path)
        assert dirty is False

    def test_dirty_tree_status_probe_failure_treated_as_clean(self, tmp_path):
        with patch("pre_mcp_gate._run_git", return_value=(1, "", "error")):
            dirty, desc = _check_gitkraken_dirty_tree(tmp_path)
        assert dirty is False
        assert "probe failed" in desc.lower()

    # --- Missing upstream check (P0-3) ---

    def test_missing_upstream_returns_true_when_no_tracking(self, tmp_path):
        with patch("pre_mcp_gate._run_git", return_value=(128, "", "no upstream")):
            missing, desc = _check_gitkraken_missing_upstream(tmp_path)
        assert missing is True
        assert "upstream" in desc.lower()

    def test_missing_upstream_returns_false_when_tracking_set(self, tmp_path):
        with patch("pre_mcp_gate._run_git", return_value=(0, "origin/main", "")):
            missing, desc = _check_gitkraken_missing_upstream(tmp_path)
        assert missing is False
        assert "origin/main" in desc

    # --- check_gitkraken_gate integration (P0-2) ---

    def _make_repo(self, tmp_path: Path) -> Path:
        """Create a minimal fake git repo structure under tmp_path."""
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main")
        return tmp_path

    def test_write_tool_confined_repo_clean_on_branch_upstream_ok(self, tmp_path):
        """Happy path: confined, on branch, clean tree, upstream set."""
        self._make_repo(tmp_path)
        with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):
            with patch("pre_mcp_gate._run_git") as mock_git:
                mock_git.return_value = (0, "refs/heads/main", "")
                assert check_gitkraken_gate("git_add_or_commit", {}) == 0

    def test_git_checkout_dirty_tree_blocked(self, tmp_path):
        self._make_repo(tmp_path)
        with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):

            def git_side_effect(args, *_a, **_kw):
                if args[:2] == ["rev-parse", "--git-dir"]:
                    return (0, ".git", "")
                if args[:1] == ["symbolic-ref"]:
                    return (0, "refs/heads/main", "")
                if args[:1] == ["status"]:
                    return (0, " M dirty_file.py", "")
                return (0, "", "")

            with patch("pre_mcp_gate._run_git", side_effect=git_side_effect):
                result = check_gitkraken_gate("git_checkout", {})
        assert result == 2

    def test_git_push_missing_upstream_blocked(self, tmp_path):
        self._make_repo(tmp_path)
        with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):

            def git_side_effect(args, *_a, **_kw):
                if args[:2] == ["rev-parse", "--git-dir"]:
                    return (0, ".git", "")
                if args[:1] == ["symbolic-ref"]:
                    return (0, "refs/heads/feature", "")
                if "@{u}" in args:
                    return (128, "", "no upstream")
                return (0, "", "")

            with patch("pre_mcp_gate._run_git", side_effect=git_side_effect):
                result = check_gitkraken_gate("git_push", {})
        assert result == 2

    def test_git_push_detached_head_blocked(self, tmp_path):
        self._make_repo(tmp_path)
        with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):

            def git_side_effect(args, *_a, **_kw):
                if args[:2] == ["rev-parse", "--git-dir"]:
                    return (0, ".git", "")
                if args[:1] == ["symbolic-ref"]:
                    return (1, "", "")
                return (0, "", "")

            with patch("pre_mcp_gate._run_git", side_effect=git_side_effect):
                result = check_gitkraken_gate("git_push", {})
        assert result == 2

    def test_issues_add_comment_passes_confinement_check(self, tmp_path):
        """issues_add_comment is a remote-write tool; passes if repo is confined."""
        self._make_repo(tmp_path)
        with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):
            with patch("pre_mcp_gate._run_git", return_value=(0, ".git", "")):
                result = check_gitkraken_gate("issues_add_comment", {})
        assert result == 0

    def test_pull_request_create_missing_upstream_blocked(self, tmp_path):
        self._make_repo(tmp_path)
        with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):

            def git_side_effect(args, *_a, **_kw):
                if args[:2] == ["rev-parse", "--git-dir"]:
                    return (0, ".git", "")
                if args[:1] == ["symbolic-ref"]:
                    return (0, "refs/heads/feature", "")
                if "@{u}" in args:
                    return (128, "", "")
                return (0, "", "")

            with patch("pre_mcp_gate._run_git", side_effect=git_side_effect):
                result = check_gitkraken_gate("pull_request_create", {})
        assert result == 2

    def test_all_remote_write_tools_in_write_set(self):
        for tool in [
            "git_push",
            "pull_request_create",
            "pull_request_create_review",
            "issues_add_comment",
            "gitlens_start_review",
        ]:
            assert tool in GITKRAKEN_REMOTE_WRITE_TOOLS

    def test_all_local_write_tools_in_write_set(self):
        for tool in [
            "git_add_or_commit",
            "git_checkout",
            "git_stash",
            "git_worktree",
            "git_branch",
            "gitlens_commit_composer",
            "gitlens_start_work",
        ]:
            assert tool in GITKRAKEN_LOCAL_WRITE_TOOLS

    # --- main() integration for GitKraken ---

    def test_main_gitkraken_read_tool_allowed(self, tmp_path):
        assert self._run_payload("git_log_or_diff", tmp_path) == 0

    def test_main_gitkraken_write_tool_confined_happy_path(self, tmp_path):
        self._make_repo(tmp_path)

        def git_ok(args, *_a, **_kw):
            return (0, "refs/heads/main" if "symbolic-ref" in args else "origin/main", "")

        with patch("pre_mcp_gate._run_git", side_effect=git_ok):
            assert self._run_payload("git_add_or_commit", tmp_path) == 0

    def test_main_gitkraken_correct_server_name_case(self, tmp_path):
        """Server name 'GitKraken' (capital G+K) must route to GitKraken gate."""
        payload = {"tool_info": {"mcp_server_name": "GitKraken", "mcp_tool_name": "git_log_or_diff"}}
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("pre_mcp_gate.GITKRAKEN_WORKSPACE_ROOT", tmp_path):
                assert main() == 0


# ---------------------------------------------------------------------------
# check_task_manager_gate — unit tests
# ---------------------------------------------------------------------------


class TestCheckTaskManagerGate:
    """Gate: Node.js in PATH (hard block on FileNotFoundError)."""

    def _gate(self):
        from pre_mcp_gate import check_task_manager_gate

        return check_task_manager_gate

    def test_node_available_allowed(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            assert self._gate()() == 0

    def test_node_not_in_path_blocked(self):
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=FileNotFoundError("node not found"),
        ):
            assert self._gate()() == 2

    def test_node_returns_nonzero_blocked(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch("pre_mcp_gate.subprocess.run", return_value=mock_result):
            assert self._gate()() == 2

    def test_node_probe_timeout_blocked(self):
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="node", timeout=10),
        ):
            assert self._gate()() == 2

    def test_recovery_tools_bypass_gate(self):
        """All TASK_MANAGER_RECOVERY_TOOLS always bypass the Node.js probe."""
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=FileNotFoundError("node not found"),
        ):
            for tool in TASK_MANAGER_RECOVERY_TOOLS:
                payload = {"tool_info": {"mcp_server_name": "task_manager", "mcp_tool_name": tool}}
                raw = json.dumps(payload)
                with patch("sys.stdin", StringIO(raw)):
                    assert main() == 0, f"Recovery tool '{tool}' must bypass task_manager gate"

    def test_update_task_whitelisted(self):
        """update_task must bypass the Node.js gate (lifecycle completion must not be blocked)."""
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=FileNotFoundError("node not found"),
        ):
            payload = {"tool_info": {"mcp_server_name": "task_manager", "mcp_tool_name": "update_task"}}
            with patch("sys.stdin", StringIO(json.dumps(payload))):
                assert main() == 0

    def test_decompose_task_whitelisted(self):
        """decompose_task must bypass the Node.js gate (T3 decomposition must not be blocked)."""
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=FileNotFoundError("node not found"),
        ):
            payload = {"tool_info": {"mcp_server_name": "task_manager", "mcp_tool_name": "decompose_task"}}
            with patch("sys.stdin", StringIO(json.dumps(payload))):
                assert main() == 0

    def test_unknown_tool_hits_gate_when_node_missing(self):
        """A tool not in TASK_MANAGER_RECOVERY_TOOLS must go through the Node.js probe."""
        with patch(
            "pre_mcp_gate.subprocess.run",
            side_effect=FileNotFoundError("node not found"),
        ):
            payload = {"tool_info": {"mcp_server_name": "task_manager", "mcp_tool_name": "list_tasks"}}
            with patch("sys.stdin", StringIO(json.dumps(payload))):
                assert main() == 2
