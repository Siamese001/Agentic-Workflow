#!/usr/bin/env python3
"""§0 DEFAULT ANALYSIS MODE — AST-First Gate Enforcement.

Constitutional Rule: ALL code investigation and analysis work MUST be preceded
by AST dependency graph construction per §0 DEFAULT ANALYSIS MODE.

This gate enforces that:
1. No code investigation without ADG dependency graph evidence
2. No impact analysis without graph-first discipline
3. No file selection without blast radius determination from ADG

BLOCKS commits that:
- Modify files without ADG provenance in commit message or artifacts
- Perform analysis work without dependency graph evidence
- Use forbidden low-signal search methods (grep, find, manual inspection)

PASSES commits that:
- Reference ADG artifacts (adg_*.json) in commit message
- Include dependency graph evidence in artifacts/
- Follow graph-first discipline per §3.4-§3.7
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]

# ADG artifact patterns
_ADG_ARTIFACT_PATTERNS = [
    "adg_*.json",
    "adg_failure_clusters.json",
    "adg_semantic_graph.json",
    "adg_test_surface_map.json",
    "adg_repair_*.json",
    "adg_full_*.json",
    "adg_snapshot_*.json",
]

# Forbidden patterns in commit messages (low-signal methods)
_FORBIDDEN_COMMIT_PATTERNS = [
    r"grep\s+for",
    r"find\s+.*\s+files?",
    r"manual\s+inspection",
    r"text\s+search",
    r"hunt\s+for",
    r"search\s+for\s+missing",
]

# Required patterns for analysis commits (graph-first evidence)
_REQUIRED_ANALYSIS_PATTERNS = [
    r"ADG",
    r"dependency\s+graph",
    r"blast\s+radius",
    r"graph-first",
    r"semantic\s+graph",
]

# File patterns that trigger AST-first requirement
_ANALYSIS_FILE_PATTERNS = [
    "**/test_*.py",
    "**/*_test.py",
    "agentic_core/**/*.py",
    "apps_*/**/*.py",
    "tools/**/*.py",
    "ops_scripts/**/*.py",
]


def _get_staged_files() -> list[str]:
    """Get list of staged files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _get_commit_message() -> str:
    """Get the current commit message from git."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        # Try to get from COMMIT_EDITMSG if log fails (during commit)
        commit_msg_file = _REPO_ROOT / ".git" / "COMMIT_EDITMSG"
        if commit_msg_file.exists():
            return commit_msg_file.read_text(encoding="utf-8", errors="ignore")
        return ""
    return result.stdout.strip()


def _check_adg_artifacts_exist() -> bool:
    """Check if any ADG artifacts exist in artifacts/ directory."""
    artifacts_dir = _REPO_ROOT / "artifacts"
    if not artifacts_dir.exists():
        return False

    for pattern in _ADG_ARTIFACT_PATTERNS:
        if list(artifacts_dir.rglob(pattern)):
            return True
    return False


def _is_analysis_commit(staged_files: list[str], commit_msg: str) -> bool:
    """Determine if this is an analysis/investigation commit requiring ADG."""
    # Check if commit message contains analysis keywords
    analysis_keywords = [
        "fix",
        "repair",
        "investigate",
        "analyze",
        "debug",
        "refactor",
        "impact",
        "blast radius",
        "dependency",
    ]

    msg_lower = commit_msg.lower()
    has_analysis_keyword = any(kw in msg_lower for kw in analysis_keywords)

    # Check if staged files match analysis patterns
    has_analysis_files = False
    for file_path in staged_files:
        # Skip artifact files themselves
        if "artifacts/" in file_path or file_path.endswith(".json"):
            continue
        # Check if it's a code file that would require analysis
        if file_path.endswith(".py"):
            has_analysis_files = True
            break

    return has_analysis_keyword and has_analysis_files


def _check_forbidden_patterns(commit_msg: str) -> list[str]:
    """Check for forbidden low-signal search patterns in commit message."""
    violations = []
    for pattern in _FORBIDDEN_COMMIT_PATTERNS:
        if re.search(pattern, commit_msg, re.IGNORECASE):
            violations.append(f"Forbidden pattern detected: {pattern}")
    return violations


def _check_required_patterns(commit_msg: str) -> bool:
    """Check if commit message contains required graph-first evidence."""
    for pattern in _REQUIRED_ANALYSIS_PATTERNS:
        if re.search(pattern, commit_msg, re.IGNORECASE):
            return True
    return False


def main() -> int:
    """Enforce §0 DEFAULT ANALYSIS MODE — AST-First Gate."""
    staged_files = _get_staged_files()
    if not staged_files:
        # No staged files, allow commit
        return 0

    commit_msg = _get_commit_message()

    # Check if this is an analysis commit
    if not _is_analysis_commit(staged_files, commit_msg):
        # Not an analysis commit, allow
        return 0

    # Check for forbidden patterns
    forbidden_violations = _check_forbidden_patterns(commit_msg)
    if forbidden_violations:
        print("\n[FAIL] §0 AST-First Gate — Forbidden low-signal search methods detected")
        print("\nViolations:")
        for violation in forbidden_violations:
            print(f"  - {violation}")
        print("\n§0 DEFAULT ANALYSIS MODE requires:")
        print("  - Use ADG dependency graph for code investigation")
        print("  - No grep/find/manual inspection as primary triage")
        print("  - Graph-first discipline per §3.4-§3.7")
        print("\nFix: Remove forbidden patterns and reference ADG artifacts")
        return 1

    # Check for required graph-first evidence
    has_graph_evidence = _check_required_patterns(commit_msg)
    has_adg_artifacts = _check_adg_artifacts_exist()

    if not has_graph_evidence and not has_adg_artifacts:
        print("\n[FAIL] §0 AST-First Gate — Missing ADG dependency graph evidence")
        print("\nThis commit modifies code files but lacks graph-first evidence.")
        print("\n§0 DEFAULT ANALYSIS MODE requires ONE of:")
        print("  1. Reference ADG artifacts in commit message (e.g., 'ADG cluster X')")
        print("  2. Include ADG artifacts in artifacts/ directory")
        print("  3. Mention 'dependency graph', 'blast radius', or 'graph-first'")
        print("\nForbidden approaches:")
        print("  ❌ grep for missing imports")
        print("  ❌ find files manually")
        print("  ❌ text search debugging")
        print("\nRequired approach:")
        print("  ✅ Build AST dependency graph first")
        print("  ✅ Use graph edges to trace dependencies")
        print("  ✅ Compute blast radius from graph")
        print("\nSee: .windsurf/skills/ast-first-gate/")
        return 1

    # All checks passed
    return 0


if __name__ == "__main__":
    sys.exit(main())
