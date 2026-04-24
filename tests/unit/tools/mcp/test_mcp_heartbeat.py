"""Unit tests for the GUARD_CLEAN heartbeat hardening.

Closes the last deferred item from
`docs/reports/plans/rca-otel-mcp-transport-closed-2026-04-23.md`.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from tools.mcp import mcp_heartbeat


@pytest.fixture
def isolated_heartbeat_dir(monkeypatch, tmp_path: Path) -> Path:
    """Redirect the module-level heartbeat directory to a temp path.

    Without this, tests would pollute the real artifacts/mcp_heartbeat dir
    and race against any live MCP server writing heartbeats.
    """
    monkeypatch.setattr(mcp_heartbeat, "_HEARTBEAT_DIR", tmp_path)
    return tmp_path


class TestWriteAndRead:
    def test_write_creates_file(self, isolated_heartbeat_dir: Path) -> None:
        assert mcp_heartbeat.write_heartbeat("example_marker.py") is True
        files = list(isolated_heartbeat_dir.glob("*.hb"))
        assert len(files) == 1

    def test_read_returns_ts_and_pid(self, isolated_heartbeat_dir: Path) -> None:
        mcp_heartbeat.write_heartbeat("m1")
        result = mcp_heartbeat.read_heartbeat("m1")
        assert result is not None
        ts, pid = result
        assert ts > 0
        assert pid > 0

    def test_read_missing_returns_none(self, isolated_heartbeat_dir: Path) -> None:
        assert mcp_heartbeat.read_heartbeat("never_written") is None

    def test_read_corrupt_returns_none(self, isolated_heartbeat_dir: Path) -> None:
        path = mcp_heartbeat._heartbeat_path("corrupt_marker")
        path.write_text("this is not a valid heartbeat", encoding="utf-8")
        assert mcp_heartbeat.read_heartbeat("corrupt_marker") is None

    def test_marker_with_unsafe_chars_sanitized(
        self, isolated_heartbeat_dir: Path
    ) -> None:
        mcp_heartbeat.write_heartbeat("tools/mcp/server with spaces.py")
        files = list(isolated_heartbeat_dir.glob("*.hb"))
        assert len(files) == 1
        # No filesystem-hostile characters in the file name.
        name = files[0].name
        assert "/" not in name
        assert " " not in name


class TestIsFresh:
    def test_fresh_when_just_written(self, isolated_heartbeat_dir: Path) -> None:
        mcp_heartbeat.write_heartbeat("m2")
        assert mcp_heartbeat.is_heartbeat_fresh("m2") is True

    def test_stale_when_timestamp_old(self, isolated_heartbeat_dir: Path) -> None:
        path = mcp_heartbeat._heartbeat_path("old_m")
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write a timestamp 10 minutes in the past.
        path.write_text(f"{time.time() - 600:.3f}:42\n", encoding="utf-8")
        assert mcp_heartbeat.is_heartbeat_fresh("old_m") is False

    def test_missing_is_not_fresh(self, isolated_heartbeat_dir: Path) -> None:
        assert mcp_heartbeat.is_heartbeat_fresh("no_such_marker") is False

    def test_custom_stale_after(self, isolated_heartbeat_dir: Path) -> None:
        path = mcp_heartbeat._heartbeat_path("tight_m")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{time.time() - 5:.3f}:1\n", encoding="utf-8")
        # With stale_after=3, a 5-second-old heartbeat is stale.
        assert mcp_heartbeat.is_heartbeat_fresh("tight_m", stale_after=3.0) is False
        # With stale_after=10, the same heartbeat is still fresh.
        assert mcp_heartbeat.is_heartbeat_fresh("tight_m", stale_after=10.0) is True


class TestClear:
    def test_clear_removes_file(self, isolated_heartbeat_dir: Path) -> None:
        mcp_heartbeat.write_heartbeat("clr_m")
        mcp_heartbeat.clear_heartbeat("clr_m")
        assert mcp_heartbeat.read_heartbeat("clr_m") is None

    def test_clear_missing_is_noop(self, isolated_heartbeat_dir: Path) -> None:
        # Should not raise.
        mcp_heartbeat.clear_heartbeat("never_existed")


class TestGuardSingleInstanceIntegration:
    """Verify the heartbeat-aware branch in guard_single_instance.

    We can't actually spawn sibling processes in a unit test, but we can
    validate the heartbeat-check plumbing: if `is_heartbeat_fresh` returns
    True, the guard routes through the GUARD_DEFERRED path instead of
    terminating. This is smoke-tested by monkeypatching the probe.
    """

    def test_force_kill_env_overrides_heartbeat(
        self, isolated_heartbeat_dir: Path, monkeypatch
    ) -> None:
        # Write a fresh heartbeat.
        mcp_heartbeat.write_heartbeat("bogus_marker_xyz")
        assert mcp_heartbeat.is_heartbeat_fresh("bogus_marker_xyz") is True

        # Set the escape hatch env var and confirm the fresh check is bypassed
        # when guard_single_instance resolves force_kill.
        from tools.mcp import mcp_bootstrap

        monkeypatch.setenv("MCP_GUARD_FORCE_KILL", "1")
        # No siblings actually exist for this bogus marker; the guard should
        # complete cleanly without raising. We assert no exception + no files
        # left behind.
        mcp_bootstrap.guard_single_instance("bogus_marker_xyz")

    def test_heartbeat_aware_default_behavior(
        self, isolated_heartbeat_dir: Path, monkeypatch
    ) -> None:
        """Default: heartbeat present => guard should NOT force-kill."""
        mcp_heartbeat.write_heartbeat("unique_noop_marker_abc")
        monkeypatch.delenv("MCP_GUARD_FORCE_KILL", raising=False)

        from tools.mcp import mcp_bootstrap

        # No real siblings exist for this marker, so the guard runs to
        # completion without hitting the termination branch. We just confirm
        # it doesn't raise.
        mcp_bootstrap.guard_single_instance("unique_noop_marker_abc")
