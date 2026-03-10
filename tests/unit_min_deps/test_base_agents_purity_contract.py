"""
Structural invariant: base_agents/ must contain ONLY base classes and shims.

AST-based deterministic scan. No utilities, no helper functions.
Guardian hard gate per blueprint: "STRICT IDENTITY ONLY."
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
)

ROOT = Path(__file__).resolve().parents[2]
BASE_AGENTS = ROOT / AGENTIC_CORE_DIR / "base_agents"

# Shims are allowed — they re-export from canonical locations
KNOWN_SHIMS = frozenset({"decorators.py", "timeout_decorator.py"})


def _is_shim(py_file: Path) -> bool:
    """Check if a file is a pure re-export shim (imports + __all__ only)."""
    try:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
    except (SyntaxError, UnicodeDecodeError):
        return False

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Expr, ast.Assign)):
            continue
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            return False
    return True


def _scan_non_class_files() -> list[str]:
    """Find files in base_agents/ that define non-class top-level functions."""
    violations: list[str] = []
    for py_file in BASE_AGENTS.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        if py_file.name in KNOWN_SHIMS:
            if not _is_shim(py_file):
                violations.append(f"{py_file.name}: listed as shim but contains definitions")
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        has_class = False
        has_bare_function = False
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                has_class = True
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                has_bare_function = True

        if has_bare_function and not has_class:
            violations.append(f"{py_file.name}: contains utility functions, not a base class")
    return violations


class TestBaseAgentsPurity:
    """Hard gate: base_agents/ must contain only base classes and shims."""

    def test_no_utility_files_in_base_agents(self) -> None:
        violations = _scan_non_class_files()
        assert not violations, "base_agents/ contains non-class utility files:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    def test_shims_are_pure_reexports(self) -> None:
        """Known shims must be pure re-export modules."""
        violations: list[str] = []
        for shim_name in KNOWN_SHIMS:
            shim_path = BASE_AGENTS / shim_name
            if shim_path.exists() and not _is_shim(shim_path):
                violations.append(f"{shim_name}: not a pure shim (contains definitions)")
        assert not violations, "Shims in base_agents/ contain non-shim code:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    def test_no_residual_legacy_decorators_import_in_production(self) -> None:
        """No agentic_core/ production module should import from base_agents shim."""
        # Shims themselves are allowed
        allowed = {
            "agentic_core/base_agents/decorators.py",
            "agentic_core/base_agents/__init__.py",
            "agentic_core/L5_safety/utils/decorators_util.py",
        }
        violations: list[str] = []
        for py_file in (ROOT / AGENTIC_CORE_DIR).rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            rel = str(py_file.relative_to(ROOT)).replace("\\", "/")
            if rel in allowed:
                continue
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):  # guardian: allow-silent-swallower
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module == "agentic_core.utils.decorators_base_util":
                        violations.append(f"{rel}:{node.lineno}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "agentic_core.utils.decorators_base_util":
                            violations.append(f"{rel}:{node.lineno}")
        assert not violations, (
            f"Found {len(violations)} residual base_agents.decorators imports "
            f"in agentic_core/ (should use agentic_core.utils.decorators):\n"
            + "\n".join(f"  {v}" for v in violations)
        )
