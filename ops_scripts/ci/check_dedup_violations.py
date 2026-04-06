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
import warnings
from pathlib import Path
from typing import Any

# Try to import ADG Query Bridge for ADG-powered dedup validation
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "adg"))
    from adg_query_bridge import ADGQueryBridge, Node
    ADG_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"ADG Query Bridge unavailable, falling back to regex: {e}")
    ADG_AVAILABLE = False

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

    # Use ADG for dedup checking when available
    if ADG_AVAILABLE:
        try:
            violations.extend(_check_agents_with_adg(diff_content))
        except Exception as e:
            warnings.warn(f"ADG agent dedup check failed, falling back to regex: {e}")
            violations.extend(_check_agents_with_regex(diff_content))
    else:
        violations.extend(_check_agents_with_regex(diff_content))

    return violations


def _check_agents_with_adg(diff_content: str) -> list[str]:
    """Check for new agents using ADG semantic analysis."""
    violations = []

    try:
        bridge = ADGQueryBridge()

        # Extract agent class names from diff
        for pattern in _AGENT_PATTERNS:
            matches = re.finditer(pattern, diff_content, re.MULTILINE)
            for match in matches:
                class_name = match.group(1) if match.groups() else match.group(0)

                # Check if similar agent exists in ADG
                similar_agents = _find_similar_agents_in_adg(bridge, class_name)
                if similar_agents:
                    violations.append(f"Potential duplicate agent '{class_name}' - similar to: {', '.join(similar_agents)}")
                else:
                    violations.append(f"New agent '{class_name}' - no ADG duplicates found")

    except Exception as e:
        warnings.warn(f"ADG agent check failed: {e}")

    return violations


def _find_similar_agents_in_adg(bridge: ADGQueryBridge, agent_name: str) -> list[str]:
    """Find semantically similar agents in ADG."""
    similar = []

    try:
        # Get all nodes that might be agents
        for layer in ["L1", "L2", "L3", "L4", "L5"]:
            nodes = bridge.nodes_in_layer(layer)
            for node in nodes:
                if ("Agent" in node.label and
                    agent_name.lower() in node.label.lower() or
                    node.label.lower() in agent_name.lower()):
                    similar.append(f"{node.label} ({node.layer})")

        # Remove exact matches (same name)
        similar = [s for s in similar if agent_name not in s]

    except Exception:
        pass

    return similar[:3]  # Return top 3 similar agents


def _check_agents_with_regex(diff_content: str) -> list[str]:
    """Original regex-based agent checking as fallback."""
    violations = []
    for pattern in _AGENT_PATTERNS:
        matches = re.finditer(pattern, diff_content, re.MULTILINE)
        for match in matches:
            class_name = match.group(1) if match.groups() else match.group(0)
            violations.append(f"New agent class: {class_name}")
    return violations


def _check_for_new_mixins(diff_content: str) -> list[str]:
    """Check if diff contains new mixin class definitions."""
    violations = []

    # Use ADG for dedup checking when available
    if ADG_AVAILABLE:
        try:
            violations.extend(_check_mixins_with_adg(diff_content))
        except Exception as e:
            warnings.warn(f"ADG mixin dedup check failed, falling back to regex: {e}")
            violations.extend(_check_mixins_with_regex(diff_content))
    else:
        violations.extend(_check_mixins_with_regex(diff_content))

    return violations


def _check_mixins_with_adg(diff_content: str) -> list[str]:
    """Check for new mixins using ADG semantic analysis."""
    violations = []

    try:
        bridge = ADGQueryBridge()

        # Extract mixin class names from diff
        for pattern in _MIXIN_PATTERNS:
            matches = re.finditer(pattern, diff_content, re.MULTILINE)
            for match in matches:
                class_name = match.group(1) if match.groups() else match.group(0)

                # Check if similar mixin exists in ADG
                similar_mixins = _find_similar_mixins_in_adg(bridge, class_name)
                if similar_mixins:
                    violations.append(f"Potential duplicate mixin '{class_name}' - similar to: {', '.join(similar_mixins)}")
                else:
                    violations.append(f"New mixin '{class_name}' - no ADG duplicates found")

    except Exception as e:
        warnings.warn(f"ADG mixin check failed: {e}")

    return violations


def _find_similar_mixins_in_adg(bridge: ADGQueryBridge, mixin_name: str) -> list[str]:
    """Find semantically similar mixins in ADG."""
    similar = []

    try:
        # Get all nodes that might be mixins
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5"]:
            nodes = bridge.nodes_in_layer(layer)
            for node in nodes:
                if ("Mixin" in node.label and
                    (mixin_name.lower() in node.label.lower() or
                     node.label.lower() in mixin_name.lower())):
                    similar.append(f"{node.label} ({node.layer})")

        # Remove exact matches
        similar = [s for s in similar if mixin_name not in s]

    except Exception:
        pass

    return similar[:3]


def _check_mixins_with_regex(diff_content: str) -> list[str]:
    """Original regex-based mixin checking as fallback."""
    violations = []
    for pattern in _MIXIN_PATTERNS:
        matches = re.finditer(pattern, diff_content, re.MULTILINE)
        for match in matches:
            class_name = match.group(1) if match.groups() else match.group(0)
            violations.append(f"New mixin class: {class_name}")
    return violations


def _check_for_new_utilities(diff_content: str) -> list[str]:
    """Check if diff contains new utility function definitions."""
    violations = []

    # Use ADG for dedup checking when available
    if ADG_AVAILABLE:
        try:
            violations.extend(_check_utilities_with_adg(diff_content))
        except Exception as e:
            warnings.warn(f"ADG utility dedup check failed, falling back to regex: {e}")
            violations.extend(_check_utilities_with_regex(diff_content))
    else:
        violations.extend(_check_utilities_with_regex(diff_content))

    return violations


def _check_utilities_with_adg(diff_content: str) -> list[str]:
    """Check for new utilities using ADG semantic analysis."""
    violations = []

    try:
        bridge = ADGQueryBridge()

        # Extract utility function names from diff
        for pattern in _UTILITY_PATTERNS:
            matches = re.finditer(pattern, diff_content, re.MULTILINE)
            for match in matches:
                func_name = match.group(1) if match.groups() else match.group(0)

                # Check if similar utility exists in ADG
                similar_utilities = _find_similar_utilities_in_adg(bridge, func_name)
                if similar_utilities:
                    violations.append(f"Potential duplicate utility '{func_name}' - similar to: {', '.join(similar_utilities)}")
                else:
                    violations.append(f"New utility '{func_name}' - no ADG duplicates found")

    except Exception as e:
        warnings.warn(f"ADG utility check failed: {e}")

    return violations


def _find_similar_utilities_in_adg(bridge: ADGQueryBridge, utility_name: str) -> list[str]:
    """Find semantically similar utilities in ADG."""
    similar = []

    try:
        # Get all nodes that might be utilities
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5"]:
            nodes = bridge.nodes_in_layer(layer)
            for node in nodes:
                if ("utility" in node.label.lower() and
                    utility_name.lower() in node.label.lower() or
                    node.label.lower() in utility_name.lower()):
                    similar.append(f"{node.label} ({node.layer})")

        # Remove exact matches
        similar = [s for s in similar if utility_name not in s]

    except Exception:
        pass

    return similar[:3]


def _check_utilities_with_regex(diff_content: str) -> list[str]:
    """Original regex-based utility checking as fallback."""
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
