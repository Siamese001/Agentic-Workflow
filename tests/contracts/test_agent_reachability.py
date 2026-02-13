"""Phase 6 — Reachability Gate.

Enforces:
For each reasoning Agent:
- Must be:
    (A) instantiated or imported in production code (outside tests/), OR
    (B) registered in canonical registry (agent_discovery_full.json), OR
    (C) imported by declared entrypoints.

If agent only referenced by tests/** → FAIL (test-only agent misplaced in production).

AST-only. No runtime imports. §29 non-growing debt pattern.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from tests.contracts._scanner import (
    AGENTIC_CORE,
    PROJECT_ROOT,
    check_exemption,
    collect_reasoning_agent_files,
    parse_file_ast,
    rel,
)

# Directories that count as "production code" (not test-only)
PRODUCTION_ROOTS = [
    AGENTIC_CORE,
    PROJECT_ROOT / "apps_rg",
    PROJECT_ROOT / "apps_lic",
    PROJECT_ROOT / "apps_shared",
    PROJECT_ROOT / "ops_scripts",
]

TESTS_ROOT = PROJECT_ROOT / "tests"
REGISTRY_PATH = PROJECT_ROOT / "agent_discovery_full.json"


# ── Gate logic ─────────────────────────────────────────────────────────────────
def _build_production_import_set() -> set[str]:
    """Scan production code for all imported agent class names.

    Returns set of class names that are imported/referenced in production code.
    """
    imported_names: set[str] = set()

    for root_dir in PRODUCTION_ROOTS:
        if not root_dir.exists():
            continue
        for py_file in root_dir.rglob("*.py"):
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.names:
                    for alias in node.names:
                        if alias.name.endswith("Agent"):
                            imported_names.add(alias.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        parts = alias.name.split(".")
                        if parts[-1].endswith("Agent"):
                            imported_names.add(parts[-1])

    return imported_names


def _build_registry_set() -> set[str]:
    """Load agent names from canonical registry."""
    if not REGISTRY_PATH.exists():
        return set()
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()

    names: set[str] = set()
    if isinstance(data, dict):
        for entry in data.get("agents", data.get("entries", [])):
            if isinstance(entry, dict):
                cls_name = entry.get("class_name", entry.get("name", ""))
                if cls_name:
                    names.add(cls_name)
        # Also check if it's a flat list
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    cls_name = entry.get("class_name", entry.get("name", ""))
                    if cls_name:
                        names.add(cls_name)
    return names


def _build_test_only_import_set() -> set[str]:
    """Scan tests/ for imported agent class names."""
    imported_names: set[str] = set()
    if not TESTS_ROOT.exists():
        return imported_names

    for py_file in TESTS_ROOT.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.names:
                for alias in node.names:
                    if alias.name.endswith("Agent"):
                        imported_names.add(alias.name)

    return imported_names


def _check_reachability(
    filepath: Path,
    prod_imports: set[str],
    registry_names: set[str],
    test_imports: set[str],
) -> list[str]:
    """Return list of violation descriptions. Empty list = pass."""
    issues: list[str] = []
    stem = filepath.stem  # e.g. "CodeEnforcerAgent"

    in_prod = stem in prod_imports
    in_registry = stem in registry_names
    in_tests = stem in test_imports

    if in_prod or in_registry:
        return []

    if in_tests and not in_prod and not in_registry:
        issues.append(f"test_only_agent: {stem} referenced only in tests/")
    elif not in_tests:
        issues.append(f"unreachable_agent: {stem} not referenced anywhere")
    else:
        issues.append(f"not_production_reachable: {stem}")

    return issues


# ── Known pre-existing debt ────────────────────────────────────────────────────
KNOWN_DEBT: frozenset[str] = frozenset(
    {
        "agentic_core/L0_routing/reasoning/RootCustomsAgent.py",
        "agentic_core/L3_orchestration/reasoning/DagEngineAgent.py",
        "agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py",
        "agentic_core/L4_state/reasoning/GravityStateAgent.py",
    },
)


# ── Tests ──────────────────────────────────────────────────────────────────────
def test_reachability_no_new_violations():
    """No new reachability violations beyond known debt."""
    prod_imports = _build_production_import_set()
    registry_names = _build_registry_set()
    test_imports = _build_test_only_import_set()

    violations: dict[str, list[str]] = {}
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        issues = _check_reachability(f, prod_imports, registry_names, test_imports)
        if issues:
            violations[rel(f)] = issues

    new_violations = set(violations.keys()) - KNOWN_DEBT
    if new_violations:
        details = "\n".join(f"  {k}: {violations[k]}" for k in sorted(new_violations))
        pytest.fail(f"New reachability violations:\n{details}")


def test_reachability_debt_ceiling():
    """Debt count must not exceed known ceiling (§29, §32)."""
    prod_imports = _build_production_import_set()
    registry_names = _build_registry_set()
    test_imports = _build_test_only_import_set()

    count = 0
    for f in collect_reasoning_agent_files():
        tree = parse_file_ast(f)
        if tree is None:
            continue
        exempt, _ = check_exemption(tree)
        if exempt:
            continue
        if _check_reachability(f, prod_imports, registry_names, test_imports):
            count += 1
    ceiling = len(KNOWN_DEBT)
    assert count <= ceiling, f"Reachability debt grew: actual={count}, ceiling={ceiling}"
