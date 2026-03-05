"""
Invariant test: _get_l5_agent_roster() must use canonical healer names.

Verifies that execute_ssot.py's agent roster uses the {Domain}HealerAgent
naming convention for all healer agents, not legacy names.
"""

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
EXECUTE_SSOT = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"

CANONICAL_HEALER_IMPORTS = [
    "FileClassificationHealerAgent",
    "HierarchyHealerAgent",
    "GravityLeakHealerAgent",
    "FilesystemSSOTHealerAgent",
]

LEGACY_HEALER_NAMES = [
    "FileClassificationAgent",  # was used as healer — replaced by FileClassificationHealerAgent
    "HierarchyAgent",  # was used as healer — replaced by HierarchyHealerAgent
    "GravityLeakRepairAgent",  # was used as healer — replaced by GravityLeakHealerAgent
    "FilesystemSSOTReconcilerAgent",  # was used as healer — replaced by FilesystemSSOTHealerAgent
]


def _parse_roster_function(source: str) -> ast.FunctionDef:
    """AST-parse execute_ssot.py and return the _get_l5_agent_roster FunctionDef node."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_get_l5_agent_roster":
            return node
    raise AssertionError("_get_l5_agent_roster() not found in execute_ssot.py")


def _import_names_in_function(func_node: ast.FunctionDef) -> list[str]:
    """Return all imported names inside the function body (AST-based)."""
    names = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.append(alias.asname or alias.name)
    return names


def _return_names_in_function(func_node: ast.FunctionDef) -> list[str]:
    """Return all names in the return tuple of the function (AST-based)."""
    names = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Return) and node.value:
            if isinstance(node.value, ast.Tuple):
                for elt in node.value.elts:
                    if isinstance(elt, ast.Name):
                        names.append(elt.id)
    return names


@pytest.fixture(scope="module")
def roster_func_node():
    source = EXECUTE_SSOT.read_text(encoding="utf-8")
    return _parse_roster_function(source)


class TestRosterUsesCanonicalHealerNames:
    def test_roster_imports_canonical_healer_names(self, roster_func_node):
        imported = _import_names_in_function(roster_func_node)
        for name in CANONICAL_HEALER_IMPORTS:
            assert name in imported, (
                f"_get_l5_agent_roster() must import canonical healer '{name}'. Found imports: {imported}"
            )

    def test_roster_does_not_import_legacy_healer_names(self, roster_func_node):
        imported = _import_names_in_function(roster_func_node)
        for legacy in LEGACY_HEALER_NAMES:
            assert legacy not in imported, (
                f"_get_l5_agent_roster() must NOT import legacy name '{legacy}'. "
                f"Use canonical healer name instead."
            )

    def test_roster_return_tuple_uses_canonical_names(self, roster_func_node):
        returned = _return_names_in_function(roster_func_node)
        for name in CANONICAL_HEALER_IMPORTS:
            assert name in returned, (
                f"_get_l5_agent_roster() return tuple must contain '{name}'. Found: {returned}"
            )

    def test_canonical_shim_files_exist(self):
        shim_dir = REPO_ROOT / "agentic_core" / "L5_safety" / "reasoning"
        for name in CANONICAL_HEALER_IMPORTS:
            shim_path = shim_dir / f"{name}.py"
            assert shim_path.exists(), f"Canonical shim file missing: {shim_path.relative_to(REPO_ROOT)}"

    def test_canonical_shims_are_importable(self):
        for name in CANONICAL_HEALER_IMPORTS:
            module_path = f"agentic_core.L5_safety.reasoning.{name}"
            try:
                mod = __import__(module_path, fromlist=[name])
                assert hasattr(mod, name), f"Module {module_path} does not export '{name}'"
            except ImportError as e:
                pytest.fail(f"Cannot import {module_path}: {e}")
