"""Unit tests for ``.windsurf/scripts/_serialization_sentinel.py``.

Layer 1 of the MCP serialization defense (constitutional §25). The sentinel
module records each tool dispatch to a per-session JSONL log and detects
sibling dispatches within a short time window. Any pair where one side is an
MCP call is blocked.

These tests use ``tmp_path`` + monkeypatch to redirect the log file and ensure
each test is fully isolated from real artifacts.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DIR = REPO_ROOT / ".windsurf" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def sentinel(tmp_path, monkeypatch):
    """Reload the sentinel module with isolated paths and clean env."""
    # Clean env that could affect behavior
    for var in ("MCP_SERIAL_BYPASS", "MCP_SERIAL_WINDOW_S"):
        monkeypatch.delenv(var, raising=False)
    # Stable session id so we get a deterministic log path.
    monkeypatch.setenv("VSCODE_PID", "TEST-SENTINEL")

    if "_serialization_sentinel" in sys.modules:
        del sys.modules["_serialization_sentinel"]
    mod = importlib.import_module("_serialization_sentinel")

    # Redirect artifact dir to tmp_path so we never write to real artifacts.
    monkeypatch.setattr(mod, "_artifacts", tmp_path)
    monkeypatch.setattr(mod, "_log_path", lambda: tmp_path / "dispatch_log.jsonl")
    return mod


# ---------------------------------------------------------------------------
# Single-dispatch behavior
# ---------------------------------------------------------------------------


def test_single_mcp_dispatch_passes(sentinel):
    """A lone MCP call has no sibling and must not block."""
    blocked, reason = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    assert blocked is False
    assert reason is None


def test_single_native_dispatch_passes(sentinel):
    """A lone native call must not block."""
    blocked, reason = sentinel.record_and_check(sentinel.KIND_RUN, "git status")
    assert blocked is False
    assert reason is None


def test_unknown_kind_passes(sentinel):
    """Unknown tool kinds are ignored to stay fail-open."""
    blocked, reason = sentinel.record_and_check("hypothetical_kind", "x")
    assert blocked is False
    assert reason is None


# ---------------------------------------------------------------------------
# Sibling-pair behavior — the core invariant
# ---------------------------------------------------------------------------


def _seed_sibling(mod, kind: str, identifier: str, *, pid: int) -> None:
    """Append a row directly to the log as if a different process wrote it."""
    log_path = mod._log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": time.time(), "pid": pid, "kind": kind, "id": identifier}
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def test_mcp_with_native_run_sibling_blocks(sentinel):
    """The exact pattern that caused the 2026-04-25 hang: MCP + run_command."""
    _seed_sibling(sentinel, sentinel.KIND_RUN, "echo hi", pid=os.getpid() + 1)
    blocked, reason = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    assert blocked is True
    assert reason is not None
    assert "serialization violation" in reason.lower()
    assert "constitutional §25" in reason


def test_mcp_with_native_read_sibling_blocks(sentinel):
    _seed_sibling(sentinel, sentinel.KIND_READ, "/path/to/file.py", pid=os.getpid() + 1)
    blocked, _ = sentinel.record_and_check(sentinel.KIND_MCP, "memory/mem_recall_session_start")
    assert blocked is True


def test_mcp_with_native_write_sibling_blocks(sentinel):
    _seed_sibling(sentinel, sentinel.KIND_WRITE, "/path/to/file.py", pid=os.getpid() + 1)
    blocked, _ = sentinel.record_and_check(sentinel.KIND_MCP, "notion/API-post-page")
    assert blocked is True


def test_native_with_mcp_sibling_blocks(sentinel):
    """The reverse direction also blocks: native call sees prior MCP entry."""
    _seed_sibling(sentinel, sentinel.KIND_MCP, "adg_sqlite/adg_health", pid=os.getpid() + 1)
    blocked, _ = sentinel.record_and_check(sentinel.KIND_RUN, "git log -n 1")
    assert blocked is True


def test_two_mcp_calls_in_window_blocks(sentinel):
    """Multiple MCP dispatches in one block also trigger the upstream race."""
    _seed_sibling(sentinel, sentinel.KIND_MCP, "memory/mem_recall_session_start", pid=os.getpid() + 1)
    blocked, _ = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    assert blocked is True


def test_two_native_calls_in_window_passes(sentinel):
    """Native-only batches are explicitly allowed (no MCP race possible)."""
    _seed_sibling(sentinel, sentinel.KIND_READ, "/file/a", pid=os.getpid() + 1)
    blocked, _ = sentinel.record_and_check(sentinel.KIND_RUN, "git status")
    assert blocked is False


# ---------------------------------------------------------------------------
# Time-window behavior
# ---------------------------------------------------------------------------


def test_stale_sibling_outside_window_passes(sentinel):
    """A sibling older than WINDOW_SECONDS is ignored."""
    log_path = sentinel._log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stale_ts = time.time() - (sentinel.WINDOW_SECONDS + 5.0)
    row = {"ts": stale_ts, "pid": os.getpid() + 1, "kind": sentinel.KIND_RUN, "id": "stale"}
    log_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    blocked, _ = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    assert blocked is False


def test_same_pid_self_entry_does_not_self_block(sentinel):
    """Our own previous entry in this process must never count as a sibling."""
    sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    blocked, _ = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_status")
    # Same pid → no sibling, but two MCPs from the same process within the
    # window is also unusual. Our rule says PID match disqualifies; assert that
    # behavior holds (sentinel is per-process, not per-call within a process).
    assert blocked is False


def test_pruning_drops_old_entries(sentinel):
    """Entries older than PRUNE_SECONDS are skipped during read."""
    log_path = sentinel._log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    very_old_ts = time.time() - (sentinel.PRUNE_SECONDS + 10.0)
    row = {"ts": very_old_ts, "pid": os.getpid() + 1, "kind": sentinel.KIND_MCP, "id": "ancient"}
    log_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    blocked, _ = sentinel.record_and_check(sentinel.KIND_RUN, "git status")
    assert blocked is False


# ---------------------------------------------------------------------------
# Bypass and sunset
# ---------------------------------------------------------------------------


def test_bypass_env_disables_check(sentinel, monkeypatch):
    """MCP_SERIAL_BYPASS=1 short-circuits the check (operator escape hatch)."""
    monkeypatch.setenv("MCP_SERIAL_BYPASS", "1")
    _seed_sibling(sentinel, sentinel.KIND_RUN, "echo hi", pid=os.getpid() + 1)
    blocked, reason = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    assert blocked is False
    assert reason is None


def test_retired_ttl_disables_check(sentinel, monkeypatch, tmp_path):
    """A past retired_after date sunsets the entire layer."""
    ttl = tmp_path / "ttl.json"
    ttl.write_text(json.dumps({"retired_after": "2000-01-01T00:00:00Z"}), encoding="utf-8")
    monkeypatch.setattr(sentinel, "_ttl_config", ttl)
    _seed_sibling(sentinel, sentinel.KIND_RUN, "echo hi", pid=os.getpid() + 1)
    blocked, _ = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    assert blocked is False


def test_future_ttl_keeps_check_active(sentinel, monkeypatch, tmp_path):
    """A future retired_after date does not yet sunset the check."""
    ttl = tmp_path / "ttl.json"
    ttl.write_text(json.dumps({"retired_after": "2099-01-01T00:00:00Z"}), encoding="utf-8")
    monkeypatch.setattr(sentinel, "_ttl_config", ttl)
    _seed_sibling(sentinel, sentinel.KIND_RUN, "echo hi", pid=os.getpid() + 1)
    blocked, _ = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    assert blocked is True


# ---------------------------------------------------------------------------
# block_if_violation convenience wrapper
# ---------------------------------------------------------------------------


def test_block_if_violation_returns_zero_when_safe(sentinel):
    rc = sentinel.block_if_violation(sentinel.KIND_MCP, "adg_sqlite/adg_health", gate_name="t")
    assert rc == 0


def test_block_if_violation_returns_two_when_paired(sentinel, capsys):
    _seed_sibling(sentinel, sentinel.KIND_RUN, "echo hi", pid=os.getpid() + 1)
    rc = sentinel.block_if_violation(sentinel.KIND_MCP, "adg_sqlite/adg_health", gate_name="t")
    assert rc == 2
    captured = capsys.readouterr()
    assert "[t] BLOCKED" in captured.err


# ---------------------------------------------------------------------------
# Defensive: malformed log lines must not crash
# ---------------------------------------------------------------------------


def test_malformed_log_lines_are_ignored(sentinel):
    log_path = sentinel._log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "this is not json\n"
        '{"missing_ts": true}\n'
        '"a string row"\n'
        + json.dumps({"ts": time.time(), "pid": os.getpid() + 1, "kind": sentinel.KIND_RUN, "id": "real"})
        + "\n",
        encoding="utf-8",
    )
    blocked, _ = sentinel.record_and_check(sentinel.KIND_MCP, "adg_sqlite/adg_health")
    # Only the well-formed sibling counts; that one IS a violation, so block.
    assert blocked is True
