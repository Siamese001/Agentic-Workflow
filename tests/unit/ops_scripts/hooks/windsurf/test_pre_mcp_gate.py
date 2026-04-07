"""
Tests for ops_scripts/hooks/windsurf/pre_mcp_gate.py (Phase 1.3).

Covers:
  - Non-ADG server → always allowed (exit 0)
  - ADG server, no lock, fresh snapshot → allowed
  - ADG server, WAL lock present → blocked (exit 2)
  - ADG server, journal lock present → blocked (exit 2)
  - ADG server, stale snapshot (>30 min) → blocked (exit 2)
  - ADG server, fresh snapshot → allowed
  - ADG server, no snapshot → allowed (no data = not stale)
  - Empty stdin → allowed (fail-open for ambiguous)
  - Malformed JSON → allowed (fail-open for ambiguous)
  - Missing mcp_server_name → allowed
"""

import json
import sys
import time
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.pre_mcp_gate import (
    check_adg_gate,
    main,
    _is_sqlite_locked,
    _get_latest_snapshot_age_seconds,
)


class TestIsSqliteLocked:
    def test_no_adg_dir(self, tmp_path):
        assert _is_sqlite_locked(tmp_path) is False

    def test_no_wal_no_journal(self, tmp_path):
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


class TestGetSnapshotAge:
    def test_no_adg_dir_returns_none(self, tmp_path):
        assert _get_latest_snapshot_age_seconds(tmp_path) is None

    def test_no_snapshots_returns_none(self, tmp_path):
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        assert _get_latest_snapshot_age_seconds(tmp_path) is None

    def test_fresh_snapshot_low_age(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_20260101.json"
        snap.write_text("{}")
        age = _get_latest_snapshot_age_seconds(tmp_path)
        assert age is not None
        assert age < 10

    def test_stale_snapshot_high_age(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_20260101.json"
        snap.write_text("{}")
        old_time = time.time() - 3600  # 1 hour ago
        import os
        os.utime(str(snap), (old_time, old_time))
        age = _get_latest_snapshot_age_seconds(tmp_path)
        assert age is not None
        assert age > 3500


class TestCheckAdgGate:
    def test_no_lock_fresh_snapshot_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_now.json"
        snap.write_text("{}")
        assert check_adg_gate(tmp_path) == 0

    def test_wal_lock_blocks(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_x.sqlite").write_text("")
        (adg / "adg_indexed_x.sqlite-wal").write_text("")
        snap = adg / "adg_snapshot_now.json"
        snap.write_text("{}")
        assert check_adg_gate(tmp_path) == 2

    def test_stale_snapshot_blocks(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        snap = adg / "adg_snapshot_old.json"
        snap.write_text("{}")
        old_time = time.time() - 3600
        import os
        os.utime(str(snap), (old_time, old_time))
        assert check_adg_gate(tmp_path) == 2

    def test_no_snapshot_allowed(self, tmp_path):
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        assert check_adg_gate(tmp_path) == 0


class TestMain:
    def _run(self, payload: dict) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            return main()

    def test_non_adg_server_allowed(self):
        payload = {"tool_info": {"mcp_server_name": "filesystem", "mcp_tool_name": "read_file"}}
        assert self._run(payload) == 0

    def test_brave_search_allowed(self):
        payload = {"tool_info": {"mcp_server_name": "brave-search"}}
        assert self._run(payload) == 0

    def test_empty_server_name_allowed(self):
        payload = {"tool_info": {}}
        assert self._run(payload) == 0

    def test_empty_stdin_allowed(self):
        with patch("sys.stdin", StringIO("")):
            assert main() == 0

    def test_malformed_json_allowed(self):
        with patch("sys.stdin", StringIO("{bad}")):
            assert main() == 0

    def test_adg_server_no_lock_fresh_allowed(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_snapshot_now.json").write_text("{}")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite"}}
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("ops_scripts.hooks.windsurf.pre_mcp_gate.REPO_ROOT", tmp_path):
                result = main()
        assert result == 0

    def test_adg_server_locked_blocked(self, tmp_path):
        adg = tmp_path / "artifacts" / "adg"
        adg.mkdir(parents=True)
        (adg / "adg_indexed_x.sqlite").write_text("")
        (adg / "adg_indexed_x.sqlite-wal").write_text("")
        (adg / "adg_snapshot_now.json").write_text("{}")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite"}}
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("ops_scripts.hooks.windsurf.pre_mcp_gate.REPO_ROOT", tmp_path):
                result = main()
        assert result == 2
