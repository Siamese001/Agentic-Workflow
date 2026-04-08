"""
EXHAUSTIVE tests for pre_mcp_gate.py (Phase 1.3) — PP-1, PP-10.

Plan requirements verified:
  - Filesystem MCP write tools (write_file, edit_file): exit 2 (BLOCKED)
  - Filesystem MCP read tools (read_text_file, list_directory, etc.): exit 0 (allowed)
  - Filesystem MCP with no tool name: exit 0 (allowed — read assumed)
  - Non-ADG, non-filesystem MCPs: always exit 0 (fail-open)
  - ADG MCP + recovery tools: always exit 0 (whitelist)
  - ADG MCP + SQLite WAL lock: exit 2 (block)
  - ADG MCP + SQLite journal lock: exit 2 (block)
  - ADG MCP + stale snapshot (>30 min): exit 2 (block)
  - ADG MCP + fresh snapshot + no lock: exit 0 (allow)
  - ADG MCP + no snapshot at all: exit 0 (allow — fail-open on missing)
  - ADG MCP + no artifacts/adg dir: exit 0 (allow — fail-open)
  - All recovery tools whitelisted: adg_health, adg_status, adg_close_connections, adg_reopen_connections
  - Empty stdin: exit 0 (non-ADG assumed, fail-open)
  - Malformed JSON: exit 0 (fail-open for non-ADG)
  - Missing server name: exit 0
  - Flat payload: handled
  - Multiple sqlite files, only one locked: still blocks
  - Lock detection: both -wal and -journal
"""

import json
import os
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
    FILESYSTEM_WRITE_TOOLS,
    _get_latest_snapshot_age_seconds,
    _is_sqlite_locked,
    check_adg_gate,
    check_filesystem_write_gate,
    main,
)


# ---------------------------------------------------------------------------
# _is_sqlite_locked
# ---------------------------------------------------------------------------


class TestIsSqliteLocked:
    def test_no_artifacts_dir_returns_false(self, tmp_path):
        assert _is_sqlite_locked(tmp_path) is False

    def test_no_sqlite_files_returns_false(self, tmp_path):
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        assert _is_sqlite_locked(tmp_path) is False

    def test_sqlite_no_wal_no_journal_returns_false(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_20260101.sqlite").write_text("")
        assert _is_sqlite_locked(tmp_path) is False

    def test_wal_file_detected(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_20260101.sqlite").write_text("")
        (adg / "adg_indexed_20260101.sqlite-wal").write_text("")
        assert _is_sqlite_locked(tmp_path) is True

    def test_journal_file_detected(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_20260101.sqlite").write_text("")
        (adg / "adg_indexed_20260101.sqlite-journal").write_text("")
        assert _is_sqlite_locked(tmp_path) is True

    def test_multiple_sqlite_one_locked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_001.sqlite").write_text("")
        (adg / "adg_indexed_002.sqlite").write_text("")
        (adg / "adg_indexed_002.sqlite-wal").write_text("")
        assert _is_sqlite_locked(tmp_path) is True

    def test_multiple_sqlite_none_locked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_001.sqlite").write_text("")
        (adg / "adg_indexed_002.sqlite").write_text("")
        assert _is_sqlite_locked(tmp_path) is False

    def test_non_adg_wal_file_not_detected(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "other_db.sqlite").write_text("")
        (adg / "other_db.sqlite-wal").write_text("")
        # non adg_indexed_ prefix — should not trigger
        assert _is_sqlite_locked(tmp_path) is False


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
    def test_fresh_snapshot_no_lock_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_snapshot_now.json").write_text("{}")
        assert check_adg_gate(tmp_path) == 0

    def test_wal_lock_blocks(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_x.sqlite").write_text("")
        (adg / "adg_indexed_x.sqlite-wal").write_text("")
        (adg / "adg_snapshot_now.json").write_text("{}")
        assert check_adg_gate(tmp_path) == 2

    def test_journal_lock_blocks(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_x.sqlite").write_text("")
        (adg / "adg_indexed_x.sqlite-journal").write_text("")
        (adg / "adg_snapshot_now.json").write_text("{}")
        assert check_adg_gate(tmp_path) == 2

    def test_stale_snapshot_blocks(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_old.json"
        snap.write_text("{}")
        os.utime(str(snap), (time.time() - 3700, time.time() - 3700))
        assert check_adg_gate(tmp_path) == 2

    def test_missing_snapshot_allowed(self, tmp_path):
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        assert check_adg_gate(tmp_path) == 0

    def test_missing_artifacts_dir_allowed(self, tmp_path):
        assert check_adg_gate(tmp_path) == 0

    def test_exactly_30min_old_snapshot_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_borderline.json"
        snap.write_text("{}")
        # Exactly at threshold — 29min59s = allowed
        t = time.time() - (29 * 60 + 59)
        os.utime(str(snap), (t, t))
        assert check_adg_gate(tmp_path) == 0

    def test_just_over_30min_old_snapshot_blocks(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_borderline.json"
        snap.write_text("{}")
        t = time.time() - (30 * 60 + 5)
        os.utime(str(snap), (t, t))
        assert check_adg_gate(tmp_path) == 2


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
        (adg / "adg_indexed_x.sqlite-wal").write_text("")
        for tool in ADG_RECOVERY_TOOLS:
            payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": tool}}
            result = self._run(payload, tmp_path)
            assert result == 0, f"Recovery tool {tool} should be whitelisted but was blocked"

    # ADG MCP blocking cases
    def test_adg_with_fresh_snapshot_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_snapshot_now.json").write_text("{}")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_nodes_by_layer"}}
        assert self._run(payload, tmp_path) == 0

    def test_adg_with_locked_sqlite_blocked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_x.sqlite").write_text("")
        (adg / "adg_indexed_x.sqlite-wal").write_text("")
        (adg / "adg_snapshot_now.json").write_text("{}")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        assert self._run(payload, tmp_path) == 2

    def test_adg_with_stale_snapshot_blocked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_old.json"
        snap.write_text("{}")
        os.utime(str(snap), (time.time() - 3700, time.time() - 3700))
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_edge_fanout"}}
        assert self._run(payload, tmp_path) == 2

    def test_adg_no_artifacts_dir_allowed(self, tmp_path):
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_health"}}
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
