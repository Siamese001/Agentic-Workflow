"""
Structural AST enforcement: decorator/timeout layer constraints.

This is the DEDICATED structural test that enforces the canonical decorator/timeout
architecture across the entire agentic_core tree using AST parsing.

Architecture:
    CANONICAL (SSOT):
        - agentic_core/base_agents/decorators.py  (standard_heal, HEAL_RESULT_SCHEMA)
        - agentic_core/base_agents/timeout_decorator.py  (timeout)

    BACKWARD-COMPAT SHIMS (re-export only):
        - agentic_core/L5_safety/utils/decorators_util.py
        - agentic_core/L0_routing/utils/timeout_decorator_util.py

Enforced invariants:
    1. No agentic_core module (except shims) imports from shim locations.
    2. base_agents/decorators.py and timeout_decorator.py do not import from L5/L0 shim modules.
    3. Shims import ONLY from their canonical base_agents counterpart (plus stdlib).
    4. Shims define __all__ and contain NO function/class defs (re-export only).
    5. Canonicals define their symbols locally (not imported from elsewhere).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
)

ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = ROOT / AGENTIC_CORE_DIR
BASE_AGENTS = AGENTIC_CORE / "base_agents"

pytestmark = pytest.mark.unit_min_deps

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SHIM_FILENAMES = frozenset({"decorators_util.py", "timeout_decorator_util.py"})

SHIM_MODULES = frozenset(
    {
        "agentic_core.L5_safety.utils.decorators_util",
        "agentic_core.L0_routing.utils.timeout_decorator_util",
    },
)

CANONICAL_FILES = {
    "decorators.py": AGENTIC_CORE / "utils" / "decorators_util.py",
    "timeout_decorator.py": AGENTIC_CORE / "utils" / "timeout_decorator_impl_util.py",
}

SHIM_TO_CANONICAL = {
    AGENTIC_CORE / "L5_safety" / "utils" / "decorators_util.py": "agentic_core.utils.decorators_util",
    ROOT
    / L0_ROUTING_DIR
    / "utils"
    / "timeout_decorator_util.py": "agentic_core.utils.timeout_decorator_util",
}


def _parse_file(path: Path) -> ast.Module | None:
    """Parse a Python file, returning None on failure."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None


def _collect_import_modules(tree: ast.Module) -> list[tuple[int, str]]:
    """Return (lineno, module_string) for every Import and ImportFrom node."""
    results: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            results.append((node.lineno, node.module))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                results.append((node.lineno, alias.name))
    return results


# ---------------------------------------------------------------------------
# 1A: Repo-wide — no module (except shims) imports from shim locations
# ---------------------------------------------------------------------------


class TestNoShimImportsRepoWide:
    """No agentic_core module (except the shims themselves) may import from shim paths."""

    def test_no_forbidden_imports_from_shim_locations(self) -> None:
        violations: list[str] = []

        for py_file in AGENTIC_CORE.rglob("*.py"):
            if py_file.name in SHIM_FILENAMES:
                continue

            tree = _parse_file(py_file)
            if tree is None:
                continue

            for lineno, module in _collect_import_modules(tree):
                for shim_mod in SHIM_MODULES:
                    if module == shim_mod or module.startswith(shim_mod + "."):
                        rel = py_file.relative_to(ROOT)
                        violations.append(f"{rel}:{lineno} imports {module}")

        assert not violations, (
            f"Found {len(violations)} forbidden import(s) from shim locations:\n"
            + "\n".join(f"  {v}" for v in violations[:30])
        )


# ---------------------------------------------------------------------------
# 1A (cont): base_agents canonical files must not import from shim modules
# ---------------------------------------------------------------------------


class TestCanonicalNoShimImports:
    """base_agents/decorators.py and timeout_decorator.py must not import from shim paths."""

    def test_decorators_no_shim_imports(self) -> None:
        tree = _parse_file(CANONICAL_FILES["decorators.py"])
        assert tree is not None, "Cannot parse decorators.py"
        violations = self._check(tree)
        assert not violations, "decorators.py imports from shim locations:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    def test_timeout_no_shim_imports(self) -> None:
        tree = _parse_file(CANONICAL_FILES["timeout_decorator.py"])
        assert tree is not None, "Cannot parse timeout_decorator.py"
        violations = self._check(tree)
        assert not violations, "timeout_decorator.py imports from shim locations:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    @staticmethod
    def _check(tree: ast.Module) -> list[str]:
        violations: list[str] = []
        for lineno, module in _collect_import_modules(tree):
            for shim_mod in SHIM_MODULES:
                if module == shim_mod or module.startswith(shim_mod + "."):
                    violations.append(f"line {lineno}: imports {module}")
        return violations


# ---------------------------------------------------------------------------
# 1B: Shim strictness — allowed imports + re-export only (no defs)
# ---------------------------------------------------------------------------


class TestShimStrictness:
    """Shims must import ONLY from their canonical counterpart and define no logic."""

    @pytest.mark.parametrize(
        "shim_path,allowed_module",
        list(SHIM_TO_CANONICAL.items()),
        ids=["decorators_util", "timeout_decorator_util"],
    )
    def test_shim_imports_only_canonical(
        self,
        shim_path: Path,
        allowed_module: str,
    ) -> None:
        tree = _parse_file(shim_path)
        assert tree is not None, f"Cannot parse {shim_path.name}"

        violations: list[str] = []
        for lineno, module in _collect_import_modules(tree):
            if module == "__future__":
                continue
            if module != allowed_module:
                violations.append(
                    f"line {lineno}: imports {module} (allowed: {allowed_module})",
                )

        assert not violations, f"{shim_path.name} imports from non-canonical locations:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    @pytest.mark.parametrize(
        "shim_path",
        list(SHIM_TO_CANONICAL.keys()),
        ids=["decorators_util", "timeout_decorator_util"],
    )
    def test_shim_defines_dunder_all(self, shim_path: Path) -> None:
        tree = _parse_file(shim_path)
        assert tree is not None, f"Cannot parse {shim_path.name}"

        has_all = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        has_all = True
                        break

        assert has_all, f"{shim_path.name} must define __all__"

    @pytest.mark.parametrize(
        "shim_path",
        list(SHIM_TO_CANONICAL.keys()),
        ids=["decorators_util", "timeout_decorator_util"],
    )
    def test_shim_no_function_or_class_defs(self, shim_path: Path) -> None:
        """Shims must not define any functions or classes (re-export only)."""
        tree = _parse_file(shim_path)
        assert tree is not None, f"Cannot parse {shim_path.name}"

        defs_found: list[str] = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                defs_found.append(f"line {node.lineno}: def {node.name}()")
            elif isinstance(node, ast.ClassDef):
                defs_found.append(f"line {node.lineno}: class {node.name}")

        assert not defs_found, (
            f"{shim_path.name} defines logic (shims must be re-export only):\n"
            + "\n".join(f"  {d}" for d in defs_found)
        )


# ---------------------------------------------------------------------------
# 1C: Canonical strictness — symbols defined locally (not re-exported)
# ---------------------------------------------------------------------------


class TestCanonicalDefinesLocally:
    """Canonical modules must define their symbols locally, not import them."""

    def test_decorators_defines_standard_heal_locally(self) -> None:
        """standard_heal must be a FunctionDef in decorators.py, not an import."""
        tree = _parse_file(CANONICAL_FILES["decorators.py"])
        assert tree is not None

        func_names = {
            node.name
            for node in ast.iter_child_nodes(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        }
        assert "standard_heal" in func_names, "standard_heal must be defined as a function in decorators.py"

    def test_decorators_defines_heal_result_schema_locally(self) -> None:
        """HEAL_RESULT_SCHEMA must be an assignment in decorators.py, not an import."""
        tree = _parse_file(CANONICAL_FILES["decorators.py"])
        assert tree is not None

        assigned_names: set[str] = set()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned_names.add(target.id)

        assert "HEAL_RESULT_SCHEMA" in assigned_names, (
            "HEAL_RESULT_SCHEMA must be assigned locally in decorators.py"
        )

    def test_timeout_defines_timeout_locally(self) -> None:
        """timeout must be a FunctionDef in timeout_decorator.py, not an import."""
        tree = _parse_file(CANONICAL_FILES["timeout_decorator.py"])
        assert tree is not None

        func_names = {
            node.name
            for node in ast.iter_child_nodes(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        }
        assert "timeout" in func_names, "timeout must be defined as a function in timeout_decorator.py"

    def test_decorators_defines_dunder_all(self) -> None:
        tree = _parse_file(CANONICAL_FILES["decorators.py"])
        assert tree is not None
        has_all = any(
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
            for node in ast.iter_child_nodes(tree)
        )
        assert has_all, "decorators.py must define __all__"

    def test_timeout_defines_dunder_all(self) -> None:
        tree = _parse_file(CANONICAL_FILES["timeout_decorator.py"])
        assert tree is not None
        has_all = any(
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
            for node in ast.iter_child_nodes(tree)
        )
        assert has_all, "timeout_decorator.py must define __all__"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
