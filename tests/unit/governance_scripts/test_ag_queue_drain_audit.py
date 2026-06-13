"""Tests for .claude/governance/scripts/_legacy_windsurf/post_agent_ag_queue_drain_audit.py"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
# Canonical paths — these scripts live in governance/scripts/, not _legacy_windsurf/
AUDIT_SCRIPT = REPO_ROOT / ".claude" / "governance" / "scripts" / "post_agent_ag_queue_drain_audit.py"
HELPER_PATH = REPO_ROOT / ".claude" / "governance" / "scripts" / "_author_gate_queue.py"


def _load_helper():
    spec = importlib.util.spec_from_file_location("_ag_queue_audit_test", HELPER_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_ag_queue_audit_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _run_audit(stdin_text: str, env_extra: dict | None = None, violation_log: Path | None = None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    # Redirect violation log to tmp — we patch by setting an env the script honors
    # Actually script uses a fixed path; in tests we clean up instead.
    result = subprocess.run(
        [sys.executable, str(AUDIT_SCRIPT)],
        input=stdin_text,
        text=True,
        capture_output=True,
        env=env,
        timeout=20,
        shell=False,
    )
    return result


@pytest.fixture
def isolated_state(tmp_path, monkeypatch):
    """Redirect queue helper state dir to tmp via symlink-like env injection.

    The audit script imports the helper fresh each call and uses STATE_DIR
    directly, so we can't easily monkeypatch across subprocess boundaries.
    Instead, we clean up the canonical STATE_DIR before/after each test.
    """
    canonical = REPO_ROOT / ".claude" / "state" / "author_gate_queue"
    snapshot: dict[str, str] = {}
    if canonical.exists():
        for p in canonical.iterdir():
            if p.suffix == ".jsonl":
                snapshot[p.name] = p.read_text(encoding="utf-8")
                p.unlink()
    # Clean violation log
    vlog = REPO_ROOT / "artifacts" / "governance" / "ag_queue_drain_violations.jsonl"
    vlog_snapshot = vlog.read_text(encoding="utf-8") if vlog.exists() else None
    if vlog.exists():
        vlog.unlink()
    yield canonical, vlog
    # Tear down: remove ALL files created during the test (including new ones)
    if canonical.exists():
        for p in list(canonical.iterdir()):
            if p.suffix == ".jsonl":
                try:
                    p.unlink()
                except OSError:
                    pass
    # Restore pre-existing queue state
    canonical.mkdir(parents=True, exist_ok=True)
    for fname, content in snapshot.items():
        (canonical / fname).write_text(content, encoding="utf-8")
    # Restore violation log
    if vlog_snapshot is not None:
        vlog.parent.mkdir(parents=True, exist_ok=True)
        vlog.write_text(vlog_snapshot, encoding="utf-8")
    elif vlog.exists():
        vlog.unlink()


def test_no_completion_marker_no_violation(isolated_state):
    _, vlog = isolated_state
    payload = json.dumps({"response_text": "Just a regular edit response with no completion markers."})
    r = _run_audit(payload)
    assert r.returncode == 0
    assert not vlog.exists() or vlog.read_text(encoding="utf-8").strip() == ""


def test_completion_marker_empty_queue_no_violation(isolated_state):
    _, vlog = isolated_state
    payload = json.dumps({"response_text": "WAVE_COMPLETE: W1 all phases done."})
    r = _run_audit(payload)
    assert r.returncode == 0
    assert not vlog.exists() or vlog.read_text(encoding="utf-8").strip() == ""


def test_completion_marker_pending_queue_no_packet_logs_violation(isolated_state):
    canonical, vlog = isolated_state
    # Seed a pending packet via helper
    helper = _load_helper()
    helper.enqueue("test-plan-x", {"id": "P1", "title": "test packet"})
    assert helper.pending_count("test-plan-x") == 1

    payload = json.dumps({"response_text": "WAVE_COMPLETE: W1 all phases done. Moving on to the next wave."})
    r = _run_audit(payload)
    assert r.returncode == 0
    assert vlog.exists()
    rows = [json.loads(l) for l in vlog.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(rows) >= 1
    row = rows[-1]
    assert row["reason"] == "no_packet_after_completion"
    assert "test-plan-x" in row["pending_plans"]
    assert row["severity"] == "high"


def test_completion_marker_with_packet_no_violation(isolated_state):
    canonical, vlog = isolated_state
    helper = _load_helper()
    helper.enqueue("test-plan-y", {"id": "P1", "title": "test packet"})

    payload = json.dumps({
        "response_text": (
            "WAVE_COMPLETE: W1 done.\n\n"
            "AUTHOR_GATE_PACKET: next decision\n"
            "Score: 0.85 ..."
        )
    })
    r = _run_audit(payload)
    assert r.returncode == 0
    assert not vlog.exists() or vlog.read_text(encoding="utf-8").strip() == ""


def test_bypass_env_logged_as_bypass(isolated_state):
    canonical, vlog = isolated_state
    helper = _load_helper()
    helper.enqueue("test-plan-z", {"id": "P1", "title": "test packet"})

    payload = json.dumps({"response_text": "PHASE_COMPLETE: 2.1 done."})
    r = _run_audit(payload, env_extra={"AG_QUEUE_DRAIN_BYPASS": "1"})
    assert r.returncode == 0
    assert vlog.exists()
    rows = [json.loads(l) for l in vlog.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert rows[-1]["reason"] == "bypass"


def test_legacy_hitl_packet_also_accepted(isolated_state):
    canonical, vlog = isolated_state
    helper = _load_helper()
    helper.enqueue("test-plan-legacy", {"id": "P1", "title": "t"})

    payload = json.dumps({
        "response_text": "WAVE_COMPLETE: W1. HITL_PACKET: legacy alias present."
    })
    r = _run_audit(payload)
    assert r.returncode == 0
    assert not vlog.exists() or vlog.read_text(encoding="utf-8").strip() == ""
