"""Unit tests for wave execution state helper + CLI + pre_mcp_gate integration.

Covers:
- Helper round-trip: set_active -> is_active -> clear
- Missing state file => is_active() returns None (allow)
- Malformed JSON => is_active() returns None (fail-open)
- CLI start/status/complete happy path
- pre_mcp_gate.check_notion_wave_deferral() blocks when active, allows when inactive
- NOTION_WAVE_DEFERRAL_BYPASS=1 bypasses the block
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf"
CLI_PATH = REPO_ROOT / "tools" / "windsurf" / "wave_execution_state.py"

sys.path.insert(0, str(SCRIPTS_DIR))

import _wave_execution_state as wes  # noqa: E402
import pre_mcp_gate  # noqa: E402


@pytest.fixture()
def isolated_session(tmp_path, monkeypatch):
    """Force a unique session id so the state file is per-test and point it at tmp_path."""
    monkeypatch.setenv("VSCODE_PID", f"pytest-{os.getpid()}-{tmp_path.name}")
    # Redirect the helper's artifact dir into tmp_path for full isolation.
    fake_artifact_dir = tmp_path / "artifacts" / "windsurf"
    fake_artifact_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(wes, "_ARTIFACT_DIR", fake_artifact_dir)
    yield tmp_path
    # Ensure no stray file leaks across tests
    wes.clear()


# ---------------------------------------------------------------------------
# Helper: set / is_active / clear round-trip
# ---------------------------------------------------------------------------


def test_inactive_when_no_state_file(isolated_session):
    assert wes.is_active() is None


def test_set_active_creates_state(isolated_session):
    path = wes.set_active("my-plan-abc123")
    assert path.exists()
    state = wes.is_active()
    assert state is not None
    assert state["plan"] == "my-plan-abc123"
    assert "started_at" in state
    assert "started_at_epoch" in state


def test_clear_removes_state(isolated_session):
    wes.set_active("my-plan-abc123")
    assert wes.is_active() is not None
    assert wes.clear() is True
    assert wes.is_active() is None
    # Second clear is a no-op
    assert wes.clear() is False


def test_set_active_overwrites_prior(isolated_session):
    wes.set_active("plan-one-111111")
    wes.set_active("plan-two-222222")
    state = wes.is_active()
    assert state is not None
    assert state["plan"] == "plan-two-222222"


def test_malformed_json_returns_none(isolated_session):
    path = wes.state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json", encoding="utf-8")
    assert wes.is_active() is None


def test_empty_dict_returns_none(isolated_session):
    path = wes.state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")
    assert wes.is_active() is None


def test_set_active_rejects_empty_plan(isolated_session):
    with pytest.raises(ValueError):
        wes.set_active("")
    with pytest.raises(ValueError):
        wes.set_active(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# CLI: start / status / complete
# ---------------------------------------------------------------------------


def _run_cli(args: list[str], env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(CLI_PATH)] + args,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        env=env,
    )


def test_cli_start_status_complete(isolated_session, monkeypatch):
    # Pin session id for subprocess by passing it through env_extra
    session = f"pytest-cli-{os.getpid()}"
    env = {"VSCODE_PID": session, "PLAN_REGISTRATION_BYPASS": "1"}

    # start
    r1 = _run_cli(["start", "--plan", "cli-test-abcdef"], env_extra=env)
    assert r1.returncode == 0, r1.stderr
    assert "START plan=cli-test-abcdef" in r1.stdout

    # status (active) — uses same session
    r2 = _run_cli(["status"], env_extra=env)
    assert r2.returncode == 0, r2.stderr
    payload = json.loads(r2.stdout)
    assert payload["active"] is True
    assert payload["plan"] == "cli-test-abcdef"

    # complete
    r3 = _run_cli(["complete", "--plan", "cli-test-abcdef"], env_extra=env)
    assert r3.returncode == 0, r3.stderr

    # status (inactive)
    r4 = _run_cli(["status"], env_extra=env)
    assert r4.returncode == 0
    payload2 = json.loads(r4.stdout)
    assert payload2 == {"active": False}


def test_cli_complete_without_start_is_noop(isolated_session):
    session = f"pytest-cli-noop-{os.getpid()}"
    r = _run_cli(["complete", "--plan", "ghost-plan-000000"], env_extra={"VSCODE_PID": session})
    assert r.returncode == 0
    assert "no active state to clear" in r.stdout


# ---------------------------------------------------------------------------
# pre_mcp_gate integration: check_notion_wave_deferral
# ---------------------------------------------------------------------------


def test_notion_allowed_when_inactive(isolated_session, monkeypatch):
    monkeypatch.delenv("NOTION_WAVE_DEFERRAL_BYPASS", raising=False)
    assert pre_mcp_gate.check_notion_wave_deferral("API-patch-page") == 0


def test_notion_blocked_when_active(isolated_session, monkeypatch, capsys):
    monkeypatch.delenv("NOTION_WAVE_DEFERRAL_BYPASS", raising=False)
    wes.set_active("blocked-plan-ffffff")
    rc = pre_mcp_gate.check_notion_wave_deferral("API-patch-page")
    assert rc == 2
    err = capsys.readouterr().err
    assert "blocked-plan-ffffff" in err
    assert "multi-wave plan" in err


def test_bypass_env_var_allows_through(isolated_session, monkeypatch):
    wes.set_active("bypass-plan-cccccc")
    monkeypatch.setenv("NOTION_WAVE_DEFERRAL_BYPASS", "1")
    assert pre_mcp_gate.check_notion_wave_deferral("API-patch-page") == 0


def test_clear_then_allow(isolated_session, monkeypatch):
    monkeypatch.delenv("NOTION_WAVE_DEFERRAL_BYPASS", raising=False)
    wes.set_active("temp-plan-dddddd")
    assert pre_mcp_gate.check_notion_wave_deferral("API-post-page") == 2
    wes.clear()
    assert pre_mcp_gate.check_notion_wave_deferral("API-post-page") == 0
