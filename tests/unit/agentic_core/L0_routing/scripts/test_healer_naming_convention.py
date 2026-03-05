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

# §26: shims may only contain imports, one __all__, and a docstring.
# No FunctionDef, ClassDef, Call (at module level), Conditionals, or Loops.
_FORBIDDEN_SHIM_NODE_TYPES = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.For,
    ast.While,
    ast.If,
)


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

    def test_tools_evidence_scripts_use_canonical_names(self):
        """Verify tools/evidence/ scripts use canonical healer names in display strings."""
        tools_evidence = REPO_ROOT / "tools" / "evidence"

        # Scripts that reference agent roster
        scripts_to_check = [
            tools_evidence / "_summarize_ssot_run.py",
            tools_evidence / "_run_ssot_healing.py",
        ]

        for script in scripts_to_check:
            if not script.exists():
                continue

            content = script.read_text(encoding="utf-8")

            # Check for canonical healer names
            assert "FilesystemSSOTHealerAgent" in content, (
                f"{script.name} must use 'FilesystemSSOTHealerAgent', not 'FilesystemSSOTReconcilerAgent'"
            )
            assert "FileClassificationHealerAgent" in content, (
                f"{script.name} must use 'FileClassificationHealerAgent', not 'FileClassificationAgent'"
            )
            assert "HierarchyHealerAgent" in content, (
                f"{script.name} must use 'HierarchyHealerAgent', not 'HierarchyAgent'"
            )
            assert "GravityLeakHealerAgent" in content, (
                f"{script.name} must use 'GravityLeakHealerAgent', not 'GravityLeakRepairAgent'"
            )
            assert "LocationHealerAgent" in content, (
                f"{script.name} must use 'LocationHealerAgent', not 'LocationAgent'"
            )

            # Check for legacy names (should NOT appear in agent roster strings)
            # Allow them in comments/other contexts, but not in roster display
            if "agents_roster" in content or '"registered"' in content:
                assert "FilesystemSSOTReconcilerAgent)" not in content, (
                    f"{script.name} agent roster must not use legacy 'FilesystemSSOTReconcilerAgent)'"
                )
                assert "FileClassificationAgent)" not in content, (
                    f"{script.name} agent roster must not use legacy 'FileClassificationAgent)'"
                )


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


class TestShimStructuralCompliance:
    """§26: Shim files may only contain imports, one __all__, and a docstring.
    No FunctionDef, ClassDef, Conditionals, or Loops allowed."""

    def test_shims_contain_only_allowed_nodes(self):
        """AST scan: each shim must contain no forbidden node types."""
        for name in CANONICAL_HEALER_IMPORTS:
            shim_path = _shim_file_for(name)
            assert shim_path.exists(), f"Shim missing: {shim_path}"
            source = shim_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            # Only check top-level body nodes (not inside imports)
            for node in tree.body:
                assert not isinstance(node, _FORBIDDEN_SHIM_NODE_TYPES), (
                    f"{shim_path.name}: forbidden node type {type(node).__name__} at line {node.lineno}. "
                    f"Shims must only contain imports, __all__, and a docstring."
                )

    def test_shims_have_exactly_one_all(self):
        """Each shim must export exactly one name via __all__."""
        for name in CANONICAL_HEALER_IMPORTS:
            shim_path = _shim_file_for(name)
            source = shim_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            all_assigns = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
            ]
            assert len(all_assigns) == 1, (
                f"{shim_path.name}: expected exactly 1 __all__ assignment, found {len(all_assigns)}"
            )
            # __all__ must contain exactly the canonical name
            all_value = all_assigns[0].value
            assert isinstance(all_value, ast.List), f"{shim_path.name}: __all__ must be a list literal"
            exported = [elt.value for elt in all_value.elts if isinstance(elt, ast.Constant)]
            assert exported == [name], (
                f"{shim_path.name}: __all__ must export exactly ['{name}'], got {exported}"
            )

    def test_shims_import_from_canonical_module(self):
        """Each shim must import the legacy class and re-export under the canonical name."""
        expected_sources = {
            "FileClassificationHealerAgent": "FileClassificationAgent",
            "HierarchyHealerAgent": "HierarchyAgent",
            "GravityLeakHealerAgent": "GravityLeakRepairAgent",
            "FilesystemSSOTHealerAgent": "FilesystemSSOTReconcilerAgent",
        }
        for canonical_name, legacy_name in expected_sources.items():
            shim_path = _shim_file_for(canonical_name)
            source = shim_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            # Find all ImportFrom nodes and collect aliases
            imported_as = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imported_name = alias.name
                        exported_as = alias.asname or alias.name
                        imported_as[exported_as] = imported_name
            assert canonical_name in imported_as, (
                f"{shim_path.name}: must import something as '{canonical_name}'"
            )
            assert imported_as[canonical_name] == legacy_name, (
                f"{shim_path.name}: must import '{legacy_name}' as '{canonical_name}', "
                f"got '{imported_as[canonical_name]}'"
            )

    def test_canonical_modules_do_not_import_shims(self):
        """§28: Canonical modules must not import shim modules (no layer inversion)."""
        shim_module_names = {f"agentic_core.L5_safety.reasoning.{n}" for n in CANONICAL_HEALER_IMPORTS}
        shim_file_names = {f"{n}.py" for n in CANONICAL_HEALER_IMPORTS}

        reasoning_dir = REPO_ROOT / "agentic_core" / "L5_safety" / "reasoning"
        violations = []
        for py_file in reasoning_dir.glob("*.py"):
            if py_file.name in shim_file_names:
                continue  # skip shims themselves
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module in shim_module_names:
                        violations.append(f"{py_file.name} line {node.lineno}: imports shim '{node.module}'")
        assert not violations, (
            "Canonical modules must not import shim modules (§28 layer inversion):\n" + "\n".join(violations)
        )
