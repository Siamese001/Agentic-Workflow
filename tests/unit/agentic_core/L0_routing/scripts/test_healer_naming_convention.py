"""
Invariant test: _get_l5_agent_roster() must use direct class imports.

Verifies that execute_ssot.py's agent roster uses direct module imports
for all healer/validator agents. The intermediate shim files
(FileClassificationHealerAgent, HierarchyHealerAgent, FilesystemSSOTHealerAgent)
have been deleted as part of the agent-script refactor (Phase 1).
LocationAgent deprecated shim deleted in Phase 2.

New invariants:
  - Roster imports real classes directly (no shim modules)
  - Deleted shim files no longer exist
  - state_mgr display labels are unchanged until Phase 10
"""

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
EXECUTE_SSOT = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"

# Direct class imports now used in _get_l5_agent_roster() (shims deleted, Phase 1)
CANONICAL_ROSTER_IMPORTS = [
    "FileClassificationAgent",
    "HierarchyAgent",
    "GravityLeakHealerAgent",
    "FilesystemSSOTReconcilerAgent",
]

# Shim names that were previously used as roster imports — now deleted
DELETED_SHIM_NAMES = [
    "FileClassificationHealerAgent",  # deleted Phase 1 — shim for FileClassificationAgent
    "HierarchyHealerAgent",  # deleted Phase 1 — shim for HierarchyAgent
    "FilesystemSSOTHealerAgent",  # deleted Phase 1 — shim for FilesystemSSOTReconcilerAgent
    "HierarchyValidatorAgent",  # deleted Phase 1 — thin wrapper, inlined in execute_ssot
    "LocationAgent",  # deleted Phase 2 — deprecated §26-violating shim for LocationHealerAgent
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


CANONICAL_STATE_MGR_NAMES = [
    "FilesystemSSOTHealerAgent",
    "LocationHealerAgent",
    "FileClassificationHealerAgent",
    "HierarchyHealerAgent",
    "GravityLeakHealerAgent",
]

LEGACY_STATE_MGR_NAMES = [
    "FilesystemSSOTReconcilerAgent",
    "LocationAgent",
    "FileClassificationAgent",
    "HierarchyAgent",
    "GravityLeakRepairAgent",
]


def _shim_file_for(name: str) -> Path:
    return REPO_ROOT / "agentic_core" / "L5_safety" / "reasoning" / f"{name}.py"


def _execute_ssot_source() -> str:
    return EXECUTE_SSOT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def roster_func_node():
    source = EXECUTE_SSOT.read_text(encoding="utf-8")
    return _parse_roster_function(source)


@pytest.fixture(scope="module")
def execute_ssot_source():
    return _execute_ssot_source()


class TestRosterUsesDirectImports:
    """Invariant: _get_l5_agent_roster() must import real classes directly.
    Shims deleted in Phase 1 of agent-script refactor."""

    def test_roster_imports_direct_class_names(self, roster_func_node):
        imported = _import_names_in_function(roster_func_node)
        for name in CANONICAL_ROSTER_IMPORTS:
            assert name in imported, (
                f"_get_l5_agent_roster() must import direct class '{name}'. Found imports: {imported}"
            )

    def test_roster_does_not_import_deleted_shim_names(self, roster_func_node):
        imported = _import_names_in_function(roster_func_node)
        for shim in DELETED_SHIM_NAMES:
            assert shim not in imported, (
                f"_get_l5_agent_roster() must NOT import deleted shim '{shim}'. "
                f"Use direct class import instead."
            )

    def test_roster_return_tuple_uses_direct_names(self, roster_func_node):
        returned = _return_names_in_function(roster_func_node)
        for name in CANONICAL_ROSTER_IMPORTS:
            assert name in returned, (
                f"_get_l5_agent_roster() return tuple must contain '{name}'. Found: {returned}"
            )

    def test_deleted_shim_files_do_not_exist(self):
        """Phase 1 negative invariant: deleted shim files must not exist."""
        shim_dir = REPO_ROOT / "agentic_core" / "L5_safety" / "reasoning"
        for name in DELETED_SHIM_NAMES:
            shim_path = shim_dir / f"{name}.py"
            assert not shim_path.exists(), (
                f"Deleted shim file still present: {shim_path.relative_to(REPO_ROOT)}. "
                f"Remove it as part of Phase 1."
            )

    def test_direct_classes_are_importable(self):
        """Direct class imports used in roster must be resolvable."""
        direct_class_paths = {
            "FileClassificationAgent": "agentic_core.L5_safety.reasoning.FileClassificationAgent",
            "HierarchyAgent": "agentic_core.L5_safety.reasoning.HierarchyAgent",
            "FilesystemSSOTReconcilerAgent": "agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent",
            "GravityLeakHealerAgent": "agentic_core.L5_safety.reasoning.GravityLeakHealerAgent",
        }
        for cls_name, module_path in direct_class_paths.items():
            try:
                mod = __import__(module_path, fromlist=[cls_name])
                assert hasattr(mod, cls_name), f"Module {module_path} does not export '{cls_name}'"
            except ImportError as e:
                pytest.fail(f"Cannot import {module_path}: {e}")


class TestStateMgrUsesCanonicalHealerNames:
    """Invariant: state_mgr.update_agent/complete_agent/skip_agent in execute_ssot.py
    must use canonical healer names, not legacy names, for all healer agents."""

    def test_state_mgr_calls_use_canonical_names(self, execute_ssot_source):
        """All state_mgr display label calls must use canonical healer names."""
        source = execute_ssot_source
        for name in CANONICAL_STATE_MGR_NAMES:
            assert f'"{name}"' in source, (
                f"execute_ssot.py must use canonical name '{name}' in state_mgr calls"
            )

    def test_state_mgr_calls_do_not_use_legacy_names_as_labels(self, execute_ssot_source):
        """state_mgr label calls must NOT pass legacy healer names as first argument.

        Uses AST to inspect every Call to state_mgr.update_agent / complete_agent /
        skip_agent and asserts the first string argument is not a legacy name.
        """
        tree = ast.parse(execute_ssot_source)
        legacy_set = set(LEGACY_STATE_MGR_NAMES)
        _state_mgr_methods = {"update_agent", "complete_agent", "skip_agent"}

        violations = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            # Match state_mgr.<method>(...)
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr in _state_mgr_methods):
                continue
            if not (isinstance(func.value, ast.Name) and func.value.id == "state_mgr"):
                continue
            # First positional arg must be a string literal
            if not node.args:
                continue
            first_arg = node.args[0]
            if not isinstance(first_arg, ast.Constant):
                continue
            label = first_arg.value
            if label in legacy_set:
                violations.append(
                    f"Line {node.lineno}: state_mgr.{func.attr}('{label}', ...) — "
                    f"use canonical healer name instead"
                )

        assert not violations, "Legacy healer names found in state_mgr calls:\n" + "\n".join(violations)


class TestDeletedShimsAreGone:
    """Phase 1 negative invariants: deleted shim files must not exist,
    and no remaining module imports from them."""

    def test_no_module_imports_deleted_shims(self):
        """§28: No remaining .py file may import from any deleted shim module."""
        deleted_shim_modules = {f"agentic_core.L5_safety.reasoning.{n}" for n in DELETED_SHIM_NAMES}

        reasoning_dir = REPO_ROOT / "agentic_core" / "L5_safety" / "reasoning"
        violations = []
        for py_file in reasoning_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(source, filename=str(py_file))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module in deleted_shim_modules:
                        violations.append(
                            f"{py_file.name} line {node.lineno}: imports deleted shim '{node.module}'"
                        )
        assert not violations, (
            "Some modules still import deleted shim modules (Phase 1 cleanup incomplete):\n"
            + "\n".join(violations)
        )
