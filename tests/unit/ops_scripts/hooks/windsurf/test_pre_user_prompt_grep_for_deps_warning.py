"""Smoke tests for pre_user_prompt_grep_for_deps_warning (P4)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOK = REPO_ROOT / ".claude" / "governance/scripts" / "pre_user_prompt_grep_for_deps_warning.py"


def _run(stdin: str, env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
        shell=False,
        check=False,
    )


def test_empty_stdin_exits_zero():
    assert _run("").returncode == 0


def test_malformed_json_exits_zero():
    """Garbage input produces no warning — exit 0."""
    r = _run("not-json")
    assert r.returncode == 0
    assert "ADG-FIRST INTENT DETECTED" not in r.stderr


def test_innocuous_prompt_no_warning():
    payload = json.dumps({"prompt": "What time is it?"})
    r = _run(payload)
    assert r.returncode == 0
    assert "ADG-FIRST INTENT DETECTED" not in r.stderr


def test_grep_for_imports_triggers_warning():
    payload = json.dumps({"prompt": "grep for imports of agentic_core.L0_routing"})
    r = _run(payload)
    assert r.returncode == 0
    assert "ADG-FIRST INTENT DETECTED" in r.stderr
    assert "adg_sqlite" in r.stderr


def test_who_uses_X_triggers_warning():
    payload = json.dumps({"prompt": "Who uses the SovereignBaseAgent class?"})
    r = _run(payload)
    assert r.returncode == 0
    assert "ADG-FIRST INTENT DETECTED" in r.stderr


def test_fan_in_phrasing_triggers_warning():
    payload = json.dumps({"prompt": "What's the fan-in for that module?"})
    r = _run(payload)
    assert r.returncode == 0
    assert "ADG-FIRST INTENT DETECTED" in r.stderr


def test_blast_radius_triggers_warning():
    payload = json.dumps({"prompt": "Show me the blast radius of removing this file."})
    r = _run(payload)
    assert r.returncode == 0
    assert "ADG-FIRST INTENT DETECTED" in r.stderr


def test_bypass_env_silences_warning():
    payload = json.dumps({"prompt": "grep for imports of foo"})
    r = _run(payload, env_overrides={"PRE_PROMPT_GREP_WARNING_BYPASS": "1"})
    assert r.returncode == 0
    assert "ADG-FIRST INTENT DETECTED" not in r.stderr
