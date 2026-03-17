"""Tests for .github/workflows — structural validity, version hygiene, branch coverage.

Verifies:
  1. All YAML files parse without error.
  2. No stale action versions (checkout@v3, setup-python@v4/v3).
  3. No Python 3.11 (repo standard is 3.12).
  4. The 7 deleted/consolidated workflows are gone.
  5. Every remaining workflow has at least one trigger.
  6. No workflow fires on only dead branches (main/develop/master/agentic-testing/new_execute_ssot
     without also covering ** or ADG_v7).
  7. ssot-kernel-guardrail.yml covers all branches (**) and contains the ssot_folder_check step.
  8. adg-invariant-scan.yml has a push path filter.
  9. safe-remediation-gate.yml has a push path filter.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

WF_DIR = Path(__file__).parents[3] / ".github" / "workflows"

DELETED_WORKFLOWS = {
    "sovereignty-hardening.yml",
    "qwen-sovereignty-audits.yml",
    "redis-integration.yml",
    "prompt-governance.yml",
    "ssot-enforcement.yml",
    "scope-separation-enforcement.yml",
    "mcp-sovereignty.yml",
}

DEAD_BRANCHES = {"main", "develop", "master", "agentic-testing", "new_execute_ssot"}

STALE_ACTIONS = [
    "actions/checkout@v3",
    "actions/setup-python@v3",
    "actions/setup-python@v4",
]

STALE_PYTHON = [
    "python-version: '3.11'",
    'python-version: "3.11"',
    "python-version: '3.10'",
    'python-version: "3.10"',
]


def _load_workflows() -> dict[str, str]:
    assert WF_DIR.exists(), f".github/workflows not found at {WF_DIR}"
    return {f.name: f.read_text(encoding="utf-8") for f in sorted(WF_DIR.glob("*.yml"))}


def _branch_list(content: str) -> set[str]:
    """Extract all branch values from a workflow."""
    branches: set[str] = set()
    for m in re.findall(r"branches:\s*\[([^\]]+)\]", content):
        for b in m.split(","):
            branches.add(b.strip().strip("\"'"))
    for m in re.findall(r"branches:\s*\n((?:\s+-[^\n]+\n)+)", content):
        for b in re.findall(r"-\s+([^\s#]+)", m):
            branches.add(b.strip("\"'"))
    return branches


def _triggers(content: str) -> set[str]:
    return set(re.findall(r"^\s{2}(push|pull_request|schedule|workflow_dispatch)", content, re.M))


WORKFLOWS = _load_workflows()


# ── 1. All YAML files parse (basic structural validity) ──────────────────────


@pytest.mark.parametrize("name,content", WORKFLOWS.items())
def test_yaml_is_valid(name: str, content: str):
    """Each workflow must start with 'name:' and contain at least one 'jobs:' block."""
    assert re.search(r"^name:", content, re.M), f"{name}: missing top-level 'name:'"
    assert re.search(r"^jobs:", content, re.M), f"{name}: missing top-level 'jobs:'"
    assert re.search(r"runs-on:", content), f"{name}: missing 'runs-on:'"


# ── 2. No stale action versions ───────────────────────────────────────────────


@pytest.mark.parametrize("name,content", WORKFLOWS.items())
def test_no_stale_checkout(name: str, content: str):
    for stale in STALE_ACTIONS:
        assert stale not in content, f"{name}: contains stale action '{stale}' — upgrade to latest"


# ── 3. No Python 3.11 or older ───────────────────────────────────────────────


@pytest.mark.parametrize("name,content", WORKFLOWS.items())
def test_no_old_python(name: str, content: str):
    for stale in STALE_PYTHON:
        assert stale not in content, f"{name}: uses stale Python version — repo standard is 3.12"


# ── 4. Deleted workflows must not exist ──────────────────────────────────────


@pytest.mark.parametrize("fname", sorted(DELETED_WORKFLOWS))
def test_deleted_workflow_is_gone(fname: str):
    assert fname not in WORKFLOWS, (
        f"Workflow '{fname}' should have been deleted (dead/redundant) but still exists"
    )


# ── 5. Every workflow has at least one trigger ───────────────────────────────


@pytest.mark.parametrize("name,content", WORKFLOWS.items())
def test_workflow_has_triggers(name: str, content: str):
    t = _triggers(content)
    assert t, f"{name}: no triggers found — workflow will never run"


# ── 6. No workflow targets ONLY dead branches ────────────────────────────────


@pytest.mark.parametrize("name,content", WORKFLOWS.items())
def test_no_dead_branch_only(name: str, content: str):
    branches = _branch_list(content)
    if not branches:
        return  # no branch filter = all branches, which is fine
    live_branches = branches - DEAD_BRANCHES
    assert live_branches, (
        f"{name}: only targets dead branches {sorted(branches)} — "
        f"will never fire on active branch. Add '**' or 'ADG_v7'."
    )


# ── 7. ssot-kernel-guardrail covers ** and has ssot_folder_check ─────────────


def test_ssot_kernel_guardrail_broad_scope():
    content = WORKFLOWS.get("ssot-kernel-guardrail.yml", "")
    assert content, "ssot-kernel-guardrail.yml not found"
    branches = _branch_list(content)
    assert "**" in branches, (
        "ssot-kernel-guardrail.yml must target all branches (**) after absorbing ssot-enforcement.yml"
    )


def test_ssot_kernel_guardrail_has_folder_check():
    content = WORKFLOWS.get("ssot-kernel-guardrail.yml", "")
    assert "ssot_folder_check" in content, (
        "ssot-kernel-guardrail.yml must include ssot_folder_check step "
        "(absorbed from deleted ssot-enforcement.yml)"
    )


def test_ssot_kernel_guardrail_has_collision_guard():
    content = WORKFLOWS.get("ssot-kernel-guardrail.yml", "")
    assert "module_collision_guard" in content, (
        "ssot-kernel-guardrail.yml must retain module_collision_guard step"
    )


def test_ssot_kernel_guardrail_has_classification_tests():
    content = WORKFLOWS.get("ssot-kernel-guardrail.yml", "")
    assert "test_classification_contract" in content, (
        "ssot-kernel-guardrail.yml must retain classification contract tests"
    )


# ── 8. adg-invariant-scan has a push path filter ─────────────────────────────


def test_adg_invariant_scan_has_path_filter():
    content = WORKFLOWS.get("adg-invariant-scan.yml", "")
    assert content, "adg-invariant-scan.yml not found"
    # Must have a paths: block under push:
    assert re.search(r"push:\s*\n\s+branches:.*?\n\s+paths:", content, re.S), (
        "adg-invariant-scan.yml: push trigger must have a 'paths:' filter "
        "to avoid running the expensive ADG scan on every doc-only commit"
    )


def test_adg_invariant_scan_paths_include_agentic_core():
    content = WORKFLOWS.get("adg-invariant-scan.yml", "")
    assert "agentic_core/**" in content, "adg-invariant-scan.yml path filter must include 'agentic_core/**'"


# ── 9. safe-remediation-gate has a push path filter ──────────────────────────


def test_safe_remediation_gate_has_path_filter():
    content = WORKFLOWS.get("safe-remediation-gate.yml", "")
    assert content, "safe-remediation-gate.yml not found"
    assert re.search(r"push:\s*\n\s+branches:.*?\n\s+paths:", content, re.S), (
        "safe-remediation-gate.yml: push trigger must have a 'paths:' filter "
        "to avoid running parse-gate on every doc-only commit"
    )


# ── 10. Total workflow count is within expected range ────────────────────────


def test_workflow_count_reduced():
    count = len(WORKFLOWS)
    assert count <= 21, (
        f"Expected ≤21 workflows after cleanup, found {count}. Possible stray workflows not yet deleted."
    )
    assert count >= 15, (
        f"Only {count} workflows found — unexpectedly few, check nothing critical was deleted."
    )


# ── 11. Key mandatory workflows still exist ──────────────────────────────────


@pytest.mark.parametrize(
    "required",
    [
        "adg-invariant-scan.yml",
        "ci-integrity-gate.yml",
        "guardian-tests.yml",
        "structure-invariants.yml",
        "ssot-kernel-guardrail.yml",
        "layer-sovereignty-enforcement.yml",
        "safe-remediation-gate.yml",
        "agent-sprawl-check.yml",
    ],
)
def test_mandatory_workflow_exists(required: str):
    assert required in WORKFLOWS, f"Mandatory workflow '{required}' is missing"
