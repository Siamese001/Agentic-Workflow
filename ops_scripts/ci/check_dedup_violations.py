#!/usr/bin/env python3
"""Dedup Guard — Prevent creation of duplicate agents, mixins, utilities, and constants.

Constitutional Rule: Before creating any new agent class, mixin, utility function, or
SSOT constant, MUST search for semantically equivalent symbols using AST-backed analysis.

This gate enforces that:
1. No duplicate agent classes (semantic equivalence check)
2. No duplicate mixins with overlapping functionality
3. No duplicate utility functions
4. No duplicate SSOT constants

BLOCKS commits that:
- Create new agents without dedup justification
- Add mixins that duplicate existing functionality
- Define utility functions semantically equivalent to existing ones
- Hardcode constants that exist in SSOT modules

PASSES commits that:
- Include dedup search evidence in commit message
- Reference ADG semantic graph showing no duplicates
- Document justification for new symbols when equivalents exist
"""

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)
_emit_writes_through("p1", "check_dedup_violations", "uwg_governed_write")
_emit_writes_through("p1", "check_dedup_violations", "uwg_governed_write_2")
_emit_pulls_context("p1", "check_dedup_violations", "context_retrieval")
_emit_pulls_context("p1", "check_dedup_violations", "context_retrieval_2")
emit_determinism_digest("trace_check_dedup_violations", "check_dedup_violations_dispatch")
emit_determinism_digest("trace_check_dedup_violations", "check_dedup_violations_complete")
_emit_validated_by_safety_plane("p1", "check_dedup_violations", "safety_validation")

# Repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]

# Patterns for symbols that require dedup checking
_AGENT_PATTERNS = [
    r"class\s+\w+Agent\s*\(",
    r"class\s+\w+Orchestrator\s*\(",
    r"class\s+\w+Gateway\s*\(",
]

_MIXIN_PATTERNS = [
    r"class\s+\w+Mixin\s*\(",
]

_UTILITY_PATTERNS = [
    r"def\s+(get_|set_|create_|build_|parse_|validate_|check_|ensure_)",
]

_CONSTANT_PATTERNS = [
    r"^[A-Z_]{3,}\s*=\s*[\"']",  # CONSTANT_NAME = "value"
    r"^[A-Z_]{3,}\s*=\s*Path\(",  # CONSTANT_PATH = Path(...)
]

# SSOT modules where constants should be defined
_SSOT_CONSTANT_MODULES = [
    "agentic_core/L0_routing/config/path_constants.py",
    "agentic_core/L5_safety/config/structure_blueprint/ssot.py",
    "agentic_core/L5_safety/config/structure_blueprint_config.py",
]

# Required dedup evidence keywords in commit message
_DEDUP_EVIDENCE_KEYWORDS = [
    "dedup",
    "no duplicate",
    "searched for",
    "ADG search",
    "semantic search",
    "no equivalent",
]


def _get_staged_files() -> list[str]:
    """Get list of staged Python files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip().endswith(".py")]


def _get_staged_diff(file_path: str) -> str:
    """Get staged diff for a specific file."""
    result = subprocess.run(
        ["git", "diff", "--cached", file_path],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def _get_commit_message() -> str:
    """Get the current commit message."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        commit_msg_file = _REPO_ROOT / ".git" / "COMMIT_EDITMSG"
        if commit_msg_file.exists():
            return commit_msg_file.read_text(encoding="utf-8", errors="ignore")
        return ""
    return result.stdout.strip()


def _check_for_new_agents(diff_content: str) -> list[str]:
    """Check if diff contains new agent class definitions."""
    violations = []
    for pattern in _AGENT_PATTERNS:
        matches = re.findall(pattern, diff_content, re.MULTILINE)
        if matches:
            violations.extend(matches)
    return violations


def _check_for_new_mixins(diff_content: str) -> list[str]:
    """Check if diff contains new mixin class definitions."""
    violations = []
    for pattern in _MIXIN_PATTERNS:
        matches = re.findall(pattern, diff_content, re.MULTILINE)
        if matches:
            violations.extend(matches)
    return violations


def _check_for_new_utilities(diff_content: str) -> list[str]:
    """Check if diff contains new utility function definitions."""
    violations = []
    for pattern in _UTILITY_PATTERNS:
        matches = re.findall(pattern, diff_content, re.MULTILINE)
        if matches:
            violations.extend(matches)
    return violations


def _check_for_new_constants(diff_content: str, file_path: str) -> list[str]:
    """Check if diff contains new constant definitions outside SSOT modules."""
    # Skip if file is in SSOT modules
    if any(ssot_mod in file_path for ssot_mod in _SSOT_CONSTANT_MODULES):
        return []

    violations = []
    for pattern in _CONSTANT_PATTERNS:
        matches = re.findall(pattern, diff_content, re.MULTILINE)
        if matches:
            violations.extend(matches)
    return violations


def _has_dedup_evidence(commit_msg: str) -> bool:
    """Check if commit message contains dedup search evidence."""
    msg_lower = commit_msg.lower()
    return any(keyword in msg_lower for keyword in _DEDUP_EVIDENCE_KEYWORDS)


def main() -> int:
    """Enforce dedup guard — prevent duplicate symbols."""
    staged_files = _get_staged_files()
    if not staged_files:
        return 0

    commit_msg = _get_commit_message()
    has_evidence = _has_dedup_evidence(commit_msg)

    all_violations: dict[str, list[str]] = {
        "agents": [],
        "mixins": [],
        "utilities": [],
        "constants": [],
    }

    # Check each staged file for new symbols
    for file_path in staged_files:
        diff_content = _get_staged_diff(file_path)
        if not diff_content:
            continue

        # Check for new agents
        agent_violations = _check_for_new_agents(diff_content)
        if agent_violations:
            all_violations["agents"].extend([f"{file_path}: {v}" for v in agent_violations])

        # Check for new mixins
        mixin_violations = _check_for_new_mixins(diff_content)
        if mixin_violations:
            all_violations["mixins"].extend([f"{file_path}: {v}" for v in mixin_violations])

        # Check for new utilities
        utility_violations = _check_for_new_utilities(diff_content)
        if utility_violations:
            all_violations["utilities"].extend([f"{file_path}: {v}" for v in utility_violations])

        # Check for new constants
        constant_violations = _check_for_new_constants(diff_content, file_path)
        if constant_violations:
            all_violations["constants"].extend([f"{file_path}: {v}" for v in constant_violations])

    # If no violations found, pass
    has_violations = any(all_violations.values())
    if not has_violations:
        return 0

    # If violations found but commit has dedup evidence, pass with warning
    if has_evidence:
        print("\n[WARN] Dedup Guard — New symbols detected but dedup evidence provided")
        print("\nCommit message contains dedup search evidence. Allowing commit.")
        return 0

    # Violations found and no evidence — FAIL (but this is a PROXY check only)
    print("\n[FAIL] Dedup Guard (Proxy) — New symbols detected without dedup evidence")
    print("\n[!] NOTE: This is a PROXY check. Full dedup enforcement happens in Windsurf.")
    print("    Pre-commit can only detect NEW symbols, not semantic duplicates.")
    print("\nNew symbols detected:")

    if all_violations["agents"]:
        print("\n  Agents:")
        for v in all_violations["agents"][:5]:
            print(f"    - {v}")

    if all_violations["mixins"]:
        print("\n  Mixins:")
        for v in all_violations["mixins"][:5]:
            print(f"    - {v}")

    if all_violations["utilities"]:
        print("\n  Utilities:")
        for v in all_violations["utilities"][:5]:
            print(f"    - {v}")

    if all_violations["constants"]:
        print("\n  Constants (outside SSOT):")
        for v in all_violations["constants"][:5]:
            print(f"    - {v}")

    print("\n§DEDUP-GUARD (Windsurf skill) requires:")
    print("  1. 4-step search BEFORE creation (AST, name, behavioral, registry)")
    print("  2. Document search results in DEDUP_SEARCH evidence section")
    print("  3. Decision: reuse | extend | create (with justification)")
    print("\nTo pass this pre-commit check, add to commit message:")
    print("  - 'dedup', 'no duplicate', 'searched for', or")
    print("  - 'DEDUP_SEARCH: decision=create'")
    print("\nReminder:")
    print("  [OK] Primary enforcement = Windsurf skill (BEFORE creation)")
    print("  [!] This CI gate = proxy flag only (AFTER creation)")
    print("\nSee: .windsurf/skills/dedup-guard/")

    return 1


if __name__ == "__main__":
    sys.exit(main())
