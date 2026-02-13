"""Phase 7 — Test-Only Import Ban.

Enforces:
Disallow imports in reasoning agents of:
    pytest, unittest, hypothesis, tests.*, support.*

AST-only. No runtime imports. §29 non-growing debt pattern.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.contracts._scanner import (
    FORBIDDEN_TEST_MODULES,
    FORBIDDEN_TEST_PREFIXES,
    check_exemption,
    collect_reasoning_agent_files,
    get_all_imports,
    parse_file_ast,
    rel,
)


# ── Gate logic ─────────────────────────────────────────────────────────────────
def _check_prod_hygiene(filepath: Path, tree: ast.Module) -> list[str]:
    """Return list of violation descriptions. Empty list = pass."""
    issues: list[str] = []
    imports = get_all_imports(tree)

    for module_name, lineno in imports:
        # Check direct forbidden modules
        top_module = module_name.split(".")[0]
        if top_module in FORBIDDEN_TEST_MODULES:
            issues.append(f"forbidden_import: {module_name} (line {lineno})")
            continue

        # Check forbidden prefixes
        for prefix in FORBIDDEN_TEST_PREFIXES:
            if module_name.startswith(prefix):
                issues.append(f"forbidden_import: {module_name} (line {lineno})")
                break

    return issues


# ── Known pre-existing debt ────────────────────────────────────────────────────
KNOWN_DEBT: frozenset[str] = frozenset(
    {
        # -- placeholder: populated after first discovery run --
    },
)


# ── Tests ──────────────────────────────────────────────────────────────────────
def test_prod_hygiene_no_new_violations():
    """No new test-import violations beyond known debt."""
    violations: dict[str, list[str]] = {}
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        issues = _check_prod_hygiene(f, tree)
        if issues:
            violations[rel(f)] = issues

    new_violations = set(violations.keys()) - KNOWN_DEBT
    if new_violations:
        details = "\n".join(f"  {k}: {violations[k]}" for k in sorted(new_violations))
        pytest.fail(f"New prod hygiene violations:\n{details}")


def test_prod_hygiene_debt_ceiling():
    """Debt count must not exceed known ceiling (§29, §32)."""
    count = 0
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        if _check_prod_hygiene(f, tree):
            count += 1
    ceiling = len(KNOWN_DEBT)
    assert count <= ceiling, f"Prod hygiene debt grew: actual={count}, ceiling={ceiling}"
