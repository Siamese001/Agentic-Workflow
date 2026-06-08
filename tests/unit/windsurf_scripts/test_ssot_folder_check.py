"""Unit tests for `.claude/governance/scripts/_ssot_folder_check.py` (SSOT routing helper).

Coverage:
- Forbidden roots block NEW files (scripts/, repo-root, _oneoff/, _oneshot/)
- Hook-prefix files outside .claude/governance/scripts/ are blocked
- Routing rules suggest the right canonical folder per filename pattern
- Allowlists (verify_tier*_gate.py, conftest.py, scripts/proof/**) pass
- Pre-existing files (exists=True) NEVER violate
- Non-Python files are out of scope
- Path normalization handles absolute Windows paths and forward/backslashes
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the helper importable without a package layout.
HELPER_DIR = Path(__file__).resolve().parents[3] / ".claude" / "governance/scripts"
sys.path.insert(0, str(HELPER_DIR))

import _ssot_folder_check as helper  # noqa: E402


# ----------------------------------------------------------------------------
# Pre-existing files — NEVER violate
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("path", [
    "scripts/check_anything.py",
    "totally_random_file.py",
    "tools/_oneoff/whatever.py",
    "src/post_agent_misroute.py",
])
def test_existing_file_never_violates(path: str) -> None:
    """Pre-existing files always pass — the gate is for NEW files only."""
    assert helper.decide(path, exists=True) is None


# ----------------------------------------------------------------------------
# scripts/ root — blocked unless allowlisted
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("path,suggested_prefix", [
    ("scripts/check_foo.py", "ops_scripts/ci/"),
    ("scripts/foo_gate.py", "ops_scripts/ci/"),
    ("scripts/validate_bar.py", "ops_scripts/ci/"),
    ("scripts/baz_calibration.py", "ops_scripts/calibration/"),
    ("scripts/cleanup_x.py", "ops_scripts/maintenance/"),
    ("scripts/random_utility.py", "tools/<domain>/"),
])
def test_scripts_root_blocks_new_files(path: str, suggested_prefix: str) -> None:
    v = helper.decide(path, exists=False)
    assert v is not None
    assert v.forbidden == "scripts-sprawl"
    assert v.suggested == suggested_prefix


@pytest.mark.parametrize("path", [
    "scripts/verify_tier0_enforcement_gate.py",
    "scripts/verify_tier3_runtime_proof_gate.py",
    "scripts/verify_tier_gate_hardening.py",
    "scripts/verify_all_requirements_gates.py",
    "scripts/verify_all_requirements_merkle_root.py",
    "scripts/c0_evidence_harness.py",
    "scripts/proof/run_cache_proof.py",
    "scripts/proof/otel_bootstrap.py",
])
def test_scripts_root_allowlist_passes(path: str) -> None:
    """Allowlisted legacy entrypoints under scripts/ must pass."""
    assert helper.decide(path, exists=False) is None


# ----------------------------------------------------------------------------
# Repo-root *.py — only conftest.py allowed
# ----------------------------------------------------------------------------


def test_repo_root_conftest_allowed() -> None:
    assert helper.decide("conftest.py", exists=False) is None


@pytest.mark.parametrize("path", [
    "weekly_report.py",
    "check_something.py",
    "random.py",
])
def test_repo_root_python_blocked(path: str) -> None:
    v = helper.decide(path, exists=False)
    assert v is not None
    assert v.forbidden == "repo-root-py"


# ----------------------------------------------------------------------------
# tools/_oneoff/ and tools/_oneshot/ — fully closed
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("path", [
    "tools/_oneoff/anything.py",
    "tools/_oneshot/append_x.py",
])
def test_oneoff_oneshot_blocked(path: str) -> None:
    v = helper.decide(path, exists=False)
    assert v is not None
    assert v.forbidden == "oneoff-sprawl"


# ----------------------------------------------------------------------------
# Hook-prefix files outside .claude/governance/scripts/ are misrouted
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("path", [
    "tools/post_agent_widget.py",
    "ops_scripts/ci/pre_write_extra.py",
    # NOTE: scripts/ root has higher precedence — those land under scripts-sprawl
])
def test_hook_prefix_misroute_blocked(path: str) -> None:
    v = helper.decide(path, exists=False)
    assert v is not None
    assert v.forbidden == "hook-script-misroute"
    assert v.suggested == ".claude/governance/scripts/"


def test_hook_prefix_in_canonical_folder_passes() -> None:
    assert helper.decide(".claude/governance/scripts/post_agent_new.py", exists=False) is None
    assert helper.decide(".claude/governance/scripts/pre_write_extra.py", exists=False) is None


# ----------------------------------------------------------------------------
# Canonical folders pass through cleanly
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("path", [
    "ops_scripts/ci/check_new_gate.py",
    "ops_scripts/calibration/new_binder.py",
    "ops_scripts/maintenance/purge_x.py",
    "tools/adg/something.py",
    "agentic_core/L0_routing/foo.py",
    "apps_eval/engines/bar.py",
    "tests/unit/test_x.py",
])
def test_canonical_folders_pass(path: str) -> None:
    assert helper.decide(path, exists=False) is None


# ----------------------------------------------------------------------------
# Non-Python files are out of scope
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("path", [
    "scripts/something.md",
    "scripts/data.json",
    "scripts/notes.txt",
])
def test_non_python_out_of_scope(path: str) -> None:
    assert helper.decide(path, exists=False) is None


# ----------------------------------------------------------------------------
# Path normalization handles Windows absolute paths
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("absolute", [
    r"C:\Git\Agentic-Workflow-FRESH\scripts\check_foo.py",
    "C:/Git/Agentic-Workflow-FRESH/scripts/check_foo.py",
    "C:/Git/Agentic-Workflow/scripts/check_foo.py",
    "./scripts/check_foo.py",
])
def test_path_normalization_absolute_windows(absolute: str) -> None:
    """Absolute Windows paths from Windsurf hook payloads must normalize correctly."""
    v = helper.decide(absolute, exists=False)
    assert v is not None
    assert v.forbidden == "scripts-sprawl"


# ----------------------------------------------------------------------------
# Edge cases
# ----------------------------------------------------------------------------


def test_empty_path() -> None:
    assert helper.decide("", exists=False) is None


def test_check_function_tuple_form() -> None:
    """The tuple-form `check()` API mirrors `decide()` for legacy callers."""
    blocked, msg, suggested = helper.check("scripts/check_foo.py", exists=False)
    assert blocked is True
    assert msg is not None
    assert suggested == "ops_scripts/ci/"

    blocked, msg, suggested = helper.check("ops_scripts/ci/check_foo.py", exists=False)
    assert blocked is False
    assert msg is None
    assert suggested is None
