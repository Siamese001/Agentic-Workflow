"""Tests for the agent/workflow fan-out restraint gate (.claude/hooks/pre_workflow_fanout_gate.py).

Verifies the count-decoupled trigger — only the pure-rediscovery shape (discovery-dominant
AND no plan-execution/output intent, at ANY agent count) is flagged, while verification /
migration / plan-execution / large parallel-implementation / non-Workflow calls pass
untouched — plus mode dispatch (ask / warn / block) and the bypass env, exercised end-to-end
via subprocess.
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

# ── plan-execution fan-out that ALSO discovers (should NOT trigger — execution intent) ──
# Discovery dominates the wording, but every lane also executes the plan / produces an
# output, so it is real work, not rediscovery — the count-decoupled escape valve.
_PLAN_EXECUTION_WORKFLOW = """
export const meta = { name: 'execute-plan', description: 'execute the plan and produce outputs' }
const out = await parallel([
  () => agent('Inventory the modules the plan provides, then implement the fix and produce outputs'),
  () => agent('Survey the sections from the plan and generate each deliverable'),
  () => agent('Map the routes per the plan and build the output'),
  () => agent('Catalog the gates the plan already mapped and emit the report'),
])
"""

# ── large parallel implementation, no discovery (should NOT trigger — count is not gated) ──
_PARALLEL_IMPLEMENT_WORKFLOW = """
export const meta = { name: 'implement-sections', description: 'build each section' }
const out = await parallel([
  () => agent('Implement feature A and write the code'),
  () => agent('Implement feature B and write the tests'),
  () => agent('Implement feature C and produce the output'),
  () => agent('Implement feature D and generate the artifact'),
  () => agent('Implement feature E and emit the result'),
])
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


def test_pure_rediscovery_triggers_at_any_count():
    # count is NOT gated: even a single-agent pure-rediscovery still trips the shape check
    a = gate.assess_fanout("const x = await agent('discover and inventory the repo')")
    assert a["high_scale"] is False           # one agent — not high scale…
    assert len(a["execution_signals"]) == 0   # …and no plan-execution / output intent
    assert a["triggered"] is True


def test_plan_execution_fanout_does_not_trigger():
    # discovery dominates the wording, but execution intent is present → not rediscovery
    a = gate.assess_fanout(_PLAN_EXECUTION_WORKFLOW)
    assert len(a["discovery_signals"]) >= 2
    assert len(a["execution_signals"]) >= 1
    assert a["triggered"] is False


def test_large_parallel_implementation_does_not_trigger():
    # many agents (high scale) but no discovery dominance → agent count alone never triggers
    a = gate.assess_fanout(_PARALLEL_IMPLEMENT_WORKFLOW)
    assert a["high_scale"] is True
    assert len(a["discovery_signals"]) == 0
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


def test_main_plan_execution_passes_silently():
    # a discovery-shaped fan-out that also executes the plan / produces outputs is not gated
    r = _run({"tool_name": "Workflow", "tool_input": {"script": _PLAN_EXECUTION_WORKFLOW}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_main_large_parallel_implementation_passes_silently():
    # many agents, no discovery dominance — count alone never prompts
    r = _run({"tool_name": "Workflow", "tool_input": {"script": _PARALLEL_IMPLEMENT_WORKFLOW}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_main_non_workflow_tool_ignored():
    r = _run({"tool_name": "Agent", "tool_input": {"prompt": "discover inventory survey catalog map all"}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""
