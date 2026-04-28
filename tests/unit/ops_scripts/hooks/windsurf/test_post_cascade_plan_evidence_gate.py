"""Smoke tests for post_cascade_plan_evidence_gate (P2)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOK = REPO_ROOT / ".windsurf" / "scripts" / "post_cascade_plan_evidence_gate.py"


def _run_hook(stdin_payload: str, env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin_payload,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
        shell=False,
        check=False,
    )


def test_empty_stdin_exits_zero():
    r = _run_hook("")
    assert r.returncode == 0


def test_malformed_json_exits_zero():
    """Hook must fail-open on garbage input (advisory layer above)."""
    r = _run_hook("not-json-at-all")
    # Garbage with no plan reference → 0; garbage that happens to contain
    # a plan path that doesn't exist → still 0. Either way, no block.
    assert r.returncode == 0


def test_no_plan_edit_exits_zero():
    payload = json.dumps({"response": "I edited agentic_core/L0_routing/foo.py and ran tests."})
    r = _run_hook(payload)
    assert r.returncode == 0


def test_bypass_env_skips_block():
    """PLAN_EVIDENCE_GATE_BYPASS=1 must short-circuit even with referenced plans."""
    payload = json.dumps({"response": ".windsurf/plans/nonexistent-aa1234.md"})
    r = _run_hook(payload, env_overrides={"PLAN_EVIDENCE_GATE_BYPASS": "1"})
    assert r.returncode == 0


def test_nonexistent_plan_referenced_does_not_block():
    """If the referenced plan does not exist on disk, hook does not block."""
    payload = json.dumps({"response": ".windsurf/plans/never-existed-zzzzzz.md"})
    r = _run_hook(payload)
    assert r.returncode == 0


def test_existing_plan_with_evidence_passes():
    """The plan we just authored has the evidence section — must pass."""
    payload = json.dumps(
        {
            "response": "Updated .windsurf/plans/adg-enforcement-hardening-p1-p8-7e9c4a.md "
            "with new wave structure."
        }
    )
    r = _run_hook(payload)
    # This plan has ADG_GRAPH_LAYER_EVIDENCE (we wrote it that way).
    assert r.returncode == 0


def test_plan_with_refactor_intent_missing_evidence_blocks():
    """Synthetic plan with refactor intent but no evidence section → exit 2."""
    plans_dir = REPO_ROOT / ".windsurf" / "plans"
    fake = plans_dir / "test-fake-refactor-aabbcc.md"
    try:
        fake.write_text(
            "# Fake refactor plan\n\n"
            "We will refactor agentic_core/L0_routing.\n\n"
            "No evidence section here.\n",
            encoding="utf-8",
        )
        payload = json.dumps({"response": ".windsurf/plans/test-fake-refactor-aabbcc.md"})
        r = _run_hook(payload)
        assert r.returncode == 2
        assert "BLOCKING" in r.stderr
    finally:
        if fake.exists():
            fake.unlink()
