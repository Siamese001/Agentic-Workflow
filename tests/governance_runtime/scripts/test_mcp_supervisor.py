"""Tests for the F5.2 MCP restart supervisor.

Covers:
  - Alive-only case: no respawn attempts.
  - Dead server: spawn_fn receives the right argv/spec.
  - Debounce: same server dead twice inside the interval → second call skips.
  - Dry-run: no spawn_fn calls; state not persisted.
  - No spec for a dead server: marked no_spec (not crash).
  - Config unreadable: ok=False.
  - CLI fail-closed when MCP_SUPERVISOR_ENABLED is unset AND --dry-run absent.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any

import pytest

_SUPERVISOR_PATH = Path(__file__).resolve().parents[3] / ".codex" / "governance" / "scripts" / "mcp_python_supervisor.py"

_spec = importlib.util.spec_from_file_location("_mcp_supervisor_under_test", _SUPERVISOR_PATH)
assert _spec is not None and _spec.loader is not None
supervisor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(supervisor)


def _spec_for(server_id: str) -> dict[str, Any]:
    return {
        "command": "python",
        "args": ["-u", f"tools/{server_id}_server.py"],
        "env": {"FOO": "bar"},
    }


@pytest.fixture
def state_path(tmp_path: Path) -> Path:
    return tmp_path / "state.json"


def test_all_alive_no_spawn(state_path: Path):
    calls: list[tuple[str, dict, bool]] = []

    def spawn_fn(sid, spec, dry):
        calls.append((sid, spec, dry))
        return {"status": "spawned"}

    result = supervisor.supervise(
        state_path=state_path,
        heartbeat_report={"ok": True, "alive": ["a", "b"], "dead": [], "total_checked": 2},
        spec_override={"a": _spec_for("a"), "b": _spec_for("b")},
        spawn_fn=spawn_fn,
    )
    assert result["ok"] is True
    assert result["results"] == []
    assert calls == []


def test_one_dead_respawns(state_path: Path):
    calls: list[str] = []

    def spawn_fn(sid, spec, dry):
        calls.append(sid)
        return {"server_id": sid, "status": "spawned", "pid": 12345}

    result = supervisor.supervise(
        state_path=state_path,
        heartbeat_report={"ok": True, "alive": ["a"], "dead": ["b"], "total_checked": 2},
        spec_override={"a": _spec_for("a"), "b": _spec_for("b")},
        spawn_fn=spawn_fn,
        now=1000.0,
        min_interval=30.0,
    )
    assert calls == ["b"]
    assert result["results"][0]["status"] == "spawned"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["b"] == 1000.0


def test_debounce_blocks_second_call(state_path: Path):
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"b": 995.0}), encoding="utf-8")
    calls: list[str] = []

    def spawn_fn(sid, spec, dry):
        calls.append(sid)
        return {"server_id": sid, "status": "spawned"}

    result = supervisor.supervise(
        state_path=state_path,
        heartbeat_report={"ok": True, "alive": [], "dead": ["b"], "total_checked": 1},
        spec_override={"b": _spec_for("b")},
        spawn_fn=spawn_fn,
        now=1000.0,  # only 5s after last spawn
        min_interval=30.0,
    )
    assert calls == []
    assert result["results"][0]["status"] == "debounced"


def test_dry_run_does_not_persist_state(state_path: Path):
    def spawn_fn(sid, spec, dry):
        assert dry is True
        return {"server_id": sid, "status": "dry_run", "argv": ["python"]}

    result = supervisor.supervise(
        state_path=state_path,
        heartbeat_report={"ok": True, "alive": [], "dead": ["b"], "total_checked": 1},
        spec_override={"b": _spec_for("b")},
        spawn_fn=spawn_fn,
        dry_run=True,
    )
    assert result["dry_run"] is True
    assert not state_path.exists()


def test_dead_server_without_spec_is_flagged(state_path: Path):
    result = supervisor.supervise(
        state_path=state_path,
        heartbeat_report={"ok": True, "alive": [], "dead": ["ghost"], "total_checked": 1},
        spec_override={},  # ghost has no spec (e.g. removed from config)
        spawn_fn=lambda *a, **kw: pytest.fail("spawn should not be called"),
    )
    assert result["results"][0] == {"server_id": "ghost", "status": "no_spec"}


def test_heartbeat_failure_propagates(state_path: Path):
    result = supervisor.supervise(
        state_path=state_path,
        heartbeat_report={"ok": False, "reason": "mcp_config_unreadable_or_no_python_servers"},
        spec_override={},
        spawn_fn=lambda *a, **kw: pytest.fail("spawn should not be called"),
    )
    assert result["ok"] is False
    assert "reason" in result


def test_cli_fail_closed_when_flag_missing(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
    monkeypatch.delenv("MCP_SUPERVISOR_ENABLED", raising=False)
    rc = supervisor.main(["--min-interval", "5"])
    # No dry-run, no flag → exit 3.
    assert rc == 3


def test_cli_dry_run_allowed_without_flag(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("MCP_SUPERVISOR_ENABLED", raising=False)
    # Patch the heartbeat probe to report all alive so the CLI succeeds
    # without needing a real mcp_config.json with live processes.
    monkeypatch.setattr(
        supervisor.heartbeat,
        "check",
        lambda: {"ok": True, "alive": ["a"], "dead": [], "total_checked": 1},
    )
    rc = supervisor.main(["--dry-run", "--json"])
    assert rc == 0


def test_decide_respects_interval():
    decisions = supervisor.decide(
        dead_servers=["a", "b"],
        state={"a": 999.5, "b": 900.0},
        now=1000.0,
        min_interval=30.0,
    )
    assert decisions == [("a", "debounced"), ("b", "respawn")]


def test_expand_env_vars_supports_repo_root_and_env_prefix(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AGENTIC_REPO_ROOT", "C:/Git/Agentic-Workflow-FRESH")
    monkeypatch.setenv("ADG_REDIS_URL", "redis://localhost:6379/0")

    assert supervisor._expand_env_vars("${AGENTIC_REPO_ROOT}/tools/memory/adg_memory_server.py") == (
        "C:/Git/Agentic-Workflow-FRESH/tools/memory/adg_memory_server.py"
    )
    assert supervisor._expand_env_vars("${env:ADG_REDIS_URL}") == "redis://localhost:6379/0"
