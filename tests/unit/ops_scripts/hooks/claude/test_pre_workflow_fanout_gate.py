"""Tests for the agent/workflow fan-out restraint gate (.claude/hooks/pre_workflow_fanout_gate.py).

Verifies the conservative trigger — high-scale AND discovery-dominant Workflow scripts are
flagged, while verification / migration / small / non-Workflow calls pass untouched — plus
mode dispatch (ask / warn / block) and the bypass env, exercised end-to-end via subprocess.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[5]
_HOOK = _REPO / ".claude" / "hooks" / "pre_workflow_fanout_gate.py"


def _load():
    spec = importlib.util.spec_from_file_location("pre_workflow_fanout_gate", _HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load()


# ── discovery-heavy mass fan-out (SHOULD trigger) ─────────────────────────────
_DISCOVERY_WORKFLOW = """
export const meta = { name: 'map-everything', description: 'inventory the whole repo' }
phase('Discover')
const areas = await parallel([
  () => agent('Discover and inventory all modules in agentic_core'),
  () => agent('Survey every app and catalog what exists'),
  () => agent('Map the codebase entrypoints and enumerate routes'),
  () => agent('Scan all config and list every gate'),
])
"""

# ── verification fan-out (should NOT trigger — justification dominates) ────────
_VERIFY_WORKFLOW = """
export const meta = { name: 'review-changes', description: 'verify findings' }
const results = await pipeline(DIMENSIONS,
  d => agent(d.prompt, {schema: FINDINGS}),
  review => parallel(review.findings.map(f => () =>
    agent(`Adversarially verify and refute: ${f.title}`, {schema: VERDICT})))
)
"""


def test_discovery_mass_fanout_triggers():
    a = gate.assess_fanout(_DISCOVERY_WORKFLOW)
    assert a["high_scale"] is True
    assert len(a["discovery_signals"]) >= 2
    assert a["triggered"] is True


def test_verification_fanout_does_not_trigger():
    a = gate.assess_fanout(_VERIFY_WORKFLOW)
    # verify / adversarial / refute / dimension >= discovery signals
    assert len(a["justification_signals"]) >= len(a["discovery_signals"])
    assert a["triggered"] is False


def test_small_fanout_does_not_trigger():
    a = gate.assess_fanout("const x = await agent('discover and inventory the repo')")
    assert a["high_scale"] is False
    assert a["triggered"] is False


def test_empty_script_safe():
    assert gate.assess_fanout("")["triggered"] is False


def _run(stdin_obj, env_extra=None):
    env = {**os.environ}
    # neutralize any inherited config so the test is hermetic
    env.pop("FANOUT_RESTRAINT_ENFORCE", None)
    env.pop("FANOUT_RESTRAINT_BYPASS", None)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(_HOOK)],
        input=json.dumps(stdin_obj),
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def test_main_ask_mode_emits_permission_decision():
    r = _run({"tool_name": "Workflow", "tool_input": {"script": _DISCOVERY_WORKFLOW}})
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert "fanout-restraint" in payload["hookSpecificOutput"]["permissionDecisionReason"]


def test_main_block_mode_blocks():
    r = _run(
        {"tool_name": "Workflow", "tool_input": {"script": _DISCOVERY_WORKFLOW}},
        {"FANOUT_RESTRAINT_ENFORCE": "block"},
    )
    assert r.returncode == 2
    assert "fanout-restraint" in r.stderr


def test_main_warn_mode_non_blocking():
    r = _run(
        {"tool_name": "Workflow", "tool_input": {"script": _DISCOVERY_WORKFLOW}},
        {"FANOUT_RESTRAINT_ENFORCE": "warn"},
    )
    assert r.returncode == 0
    assert "fanout-restraint" in r.stderr
    assert r.stdout.strip() == ""


def test_main_bypass():
    r = _run(
        {"tool_name": "Workflow", "tool_input": {"script": _DISCOVERY_WORKFLOW}},
        {"FANOUT_RESTRAINT_BYPASS": "1"},
    )
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_main_verification_passes_silently():
    r = _run({"tool_name": "Workflow", "tool_input": {"script": _VERIFY_WORKFLOW}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_main_non_workflow_tool_ignored():
    r = _run({"tool_name": "Agent", "tool_input": {"prompt": "discover inventory survey catalog map all"}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""
