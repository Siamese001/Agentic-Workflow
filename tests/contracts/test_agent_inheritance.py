"""Phase 2 — Base Class Contract Gate.

Enforces:
1. Agent class must inherit (directly or indirectly) from SovereignBaseAgent.
2. Reject local class shadowing named SovereignBaseAgent.
3. Reject disallowed bases (unittest.TestCase, ABC, Protocol).

AST-only resolution. No runtime imports. §29 non-growing debt pattern.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.contracts._scanner import (
    KNOWN_SOVEREIGN_BASES,
    check_exemption,
    collect_reasoning_agent_files,
    find_agent_class,
    get_class_base_names,
    get_top_level_classes,
    parse_file_ast,
    rel,
)

DISALLOWED_BASES = frozenset(
    {
        "TestCase",
        "ABC",
        "Protocol",
    },
)


# ── Gate logic ─────────────────────────────────────────────────────────────────
def _check_inheritance(filepath: Path, tree: ast.Module) -> list[str]:
    """Return list of violation descriptions. Empty list = pass."""
    issues: list[str] = []
    stem = filepath.stem

    agent_cls = find_agent_class(tree, stem)
    if agent_cls is None:
        # Try to find any Agent class
        all_classes = get_top_level_classes(tree)
        agent_classes = [c for c in all_classes if c.name.endswith("Agent") and not c.name.startswith("_")]
        if len(agent_classes) == 1:
            agent_cls = agent_classes[0]
        else:
            issues.append("no_agent_class_for_inheritance_check")
            return issues

    base_names = get_class_base_names(agent_cls)

    # 1. Must inherit from a known sovereign base
    has_sovereign_base = any(b in KNOWN_SOVEREIGN_BASES for b in base_names)
    if not has_sovereign_base:
        issues.append(f"missing_sovereign_base: bases={base_names}")

    # 2. Check for local class shadowing SovereignBaseAgent
    all_classes = get_top_level_classes(tree)
    local_class_names = {c.name for c in all_classes}
    for sov_name in KNOWN_SOVEREIGN_BASES:
        if sov_name in local_class_names and sov_name != stem:
            issues.append(f"local_shadow: {sov_name} defined locally")

    # 3. Reject disallowed bases
    for b in base_names:
        if b in DISALLOWED_BASES:
            issues.append(f"disallowed_base: {b}")

    return issues


# ── Known pre-existing debt ────────────────────────────────────────────────────
KNOWN_DEBT: frozenset[str] = frozenset(
    {
        "agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py",
        "agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py",
        "agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py",
        "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
        "agentic_core/L5_safety/reasoning/LocationAgent.py",
        "agentic_core/L5_safety/reasoning/ReportLocationAgent.py",
        "agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py",
    },
)


# ── Tests ──────────────────────────────────────────────────────────────────────
def test_inheritance_no_new_violations():
    """No new inheritance violations beyond known debt."""
    violations: dict[str, list[str]] = {}
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        issues = _check_inheritance(f, tree)
        if issues:
            violations[rel(f)] = issues

    new_violations = set(violations.keys()) - KNOWN_DEBT
    if new_violations:
        details = "\n".join(f"  {k}: {violations[k]}" for k in sorted(new_violations))
        pytest.fail(f"New inheritance violations:\n{details}")


def test_inheritance_debt_ceiling():
    """Debt count must not exceed known ceiling (§29, §32)."""
    count = 0
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        if _check_inheritance(f, tree):
            count += 1
    ceiling = len(KNOWN_DEBT)
    assert count <= ceiling, f"Inheritance debt grew: actual={count}, ceiling={ceiling}"
