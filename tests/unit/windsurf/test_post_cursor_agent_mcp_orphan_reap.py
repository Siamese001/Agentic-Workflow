"""Tests for the post_cursor_agent_mcp_orphan_reap Windsurf hook.

Invariants the hook must uphold:
    1. ALWAYS exit 0 (must never block Cursor Agent).
    2. Respect MCP_ORPHAN_REAP_BYPASS=1 (skip without invoking detector).
    3. Log exactly one JSONL record per invocation.
    4. Pass --kill --json to the detector with cohort-gap/stale-min.
    5. Parse detector JSON output and record counts + orphan pids.
    6. Survive detector timeout / spawn error / malformed JSON.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "post_cursor_agent_mcp_orphan_reap.py"


def _load_hook(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Import the hook module with LOG_PATH redirected to tmp_path."""
    spec = importlib.util.spec_from_file_location("post_cursor_agent_mcp_orphan_reap", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    log = tmp_path / "mcp_orphan_reap.jsonl"
    monkeypatch.setattr(mod, "LOG_PATH", log)
    return mod, log


def _read_log_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---- bypass path ---------------------------------------------------------


def test_bypass_env_skips_detector(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, log = _load_hook(tmp_path, monkeypatch)
    monkeypatch.setenv("MCP_ORPHAN_REAP_BYPASS", "1")
    run_mock = mock.MagicMock()
    monkeypatch.setattr(subprocess, "run", run_mock)
    rc = mod.main()
    assert rc == 0
    run_mock.assert_not_called()
    records = _read_log_records(log)
    assert len(records) == 1
    assert records[0]["action"] == "bypass"


# ---- missing detector ----------------------------------------------------


def test_missing_detector_skips_silently(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, log = _load_hook(tmp_path, monkeypatch)
    monkeypatch.delenv("MCP_ORPHAN_REAP_BYPASS", raising=False)
    monkeypatch.setattr(mod, "DETECTOR", tmp_path / "nonexistent.py")
    rc = mod.main()
    assert rc == 0
    records = _read_log_records(log)
    assert len(records) == 1
    assert records[0]["action"] == "skip"
    assert "detector missing" in records[0]["reason"]


# ---- happy path: clean scan ----------------------------------------------


def test_clean_scan_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, log = _load_hook(tmp_path, monkeypatch)
    monkeypatch.delenv("MCP_ORPHAN_REAP_BYPASS", raising=False)
    detector_out = json.dumps(
        {
            "total_procs_seen": 20,
            "mcp_procs": 11,
            "orphan_count": 0,
            "orphans": [],
        }
    )
    fake = mock.MagicMock(stdout=detector_out, stderr="", returncode=0)
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: fake)
    rc = mod.main()
    assert rc == 0
    records = _read_log_records(log)
    assert len(records) == 1
    r = records[0]
    assert r["action"] == "scan"
    assert r["orphan_count"] == 0
    assert r["mcp_procs"] == 11


# ---- orphans reaped ------------------------------------------------------


def test_orphans_reaped_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, log = _load_hook(tmp_path, monkeypatch)
    monkeypatch.delenv("MCP_ORPHAN_REAP_BYPASS", raising=False)
    detector_out = json.dumps(
        {
            "total_procs_seen": 30,
            "mcp_procs": 21,
            "orphan_count": 3,
            "orphans": [
                {"pid": 111, "started": "2026-04-23T10:00:00", "cmdline": "python tools.adg.mcp.server"},
                {"pid": 222, "started": "2026-04-23T10:00:01", "cmdline": "node filesystem_mcp_launcher.js"},
                {"pid": 333, "started": "2026-04-23T10:00:02", "cmdline": "npx notion-mcp-server"},
            ],
        }
    )
    fake = mock.MagicMock(stdout=detector_out, stderr="", returncode=0)
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: fake)
    rc = mod.main()
    assert rc == 0
    records = _read_log_records(log)
    assert len(records) == 1
    r = records[0]
    assert r["action"] == "reaped"
    assert r["orphan_count"] == 3
    assert [o["pid"] for o in r["orphans"]] == [111, 222, 333]


# ---- detector command shape (invariant #4) ------------------------------


def test_detector_called_with_kill_json_gap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, log = _load_hook(tmp_path, monkeypatch)
    monkeypatch.delenv("MCP_ORPHAN_REAP_BYPASS", raising=False)
    captured = {}

    def _fake_run(cmd, **kw):
        captured["cmd"] = cmd
        captured["kw"] = kw
        return mock.MagicMock(
            stdout='{"total_procs_seen":0,"mcp_procs":0,"orphan_count":0,"orphans":[]}',
            stderr="",
            returncode=0,
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)
    mod.main()

    cmd = captured["cmd"]
    assert "--kill" in cmd
    assert "--json" in cmd
    assert "--cohort-gap-sec" in cmd
    assert "--stale-min" in cmd
    assert captured["kw"].get("shell") is False
    assert captured["kw"].get("timeout") == 30
    assert str(mod.DETECTOR) in cmd


# ---- timeout tolerance ---------------------------------------------------


def test_detector_timeout_still_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, log = _load_hook(tmp_path, monkeypatch)
    monkeypatch.delenv("MCP_ORPHAN_REAP_BYPASS", raising=False)

    def _raise_timeout(*a, **kw):
        raise subprocess.TimeoutExpired(cmd="x", timeout=30)

    monkeypatch.setattr(subprocess, "run", _raise_timeout)
    rc = mod.main()
    assert rc == 0
    records = _read_log_records(log)
    assert records[0]["action"] == "error"
    assert records[0]["reason"] == "timeout"


# ---- spawn OSError tolerance --------------------------------------------


def test_detector_spawn_error_still_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, log = _load_hook(tmp_path, monkeypatch)
    monkeypatch.delenv("MCP_ORPHAN_REAP_BYPASS", raising=False)

    def _raise(*a, **kw):
        raise OSError("boom")

    monkeypatch.setattr(subprocess, "run", _raise)
    rc = mod.main()
    assert rc == 0
    records = _read_log_records(log)
    assert records[0]["action"] == "error"
    assert "spawn failed" in records[0]["reason"]


# ---- malformed detector output ------------------------------------------


def test_malformed_detector_json_still_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, log = _load_hook(tmp_path, monkeypatch)
    monkeypatch.delenv("MCP_ORPHAN_REAP_BYPASS", raising=False)
    fake = mock.MagicMock(stdout="not json{", stderr="", returncode=0)
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: fake)
    rc = mod.main()
    assert rc == 0
    records = _read_log_records(log)
    assert records[0]["action"] == "scan"
    # Missing parsed data is recorded as None — no crash.
    assert records[0]["orphan_count"] is None


# ---- hooks.json wiring --------------------------------------------------


def test_hook_is_registered_in_hooks_json() -> None:
    """Regression guard: the hook must be wired into post_cursor_agent_response."""
    hooks_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "hooks.json"
    data = json.loads(hooks_path.read_text(encoding="utf-8"))
    entries = data["hooks"]["post_cursor_agent_response"]
    commands = [e["command"] for e in entries]
    assert any("post_cursor_agent_mcp_orphan_reap.py" in c for c in commands), (
        "post_cursor_agent_mcp_orphan_reap.py must be registered in "
        ".cursor/hooks.json post_cursor_agent_response chain"
    )
