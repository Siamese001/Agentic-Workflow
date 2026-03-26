"""
Structural invariant: base_agents/ must contain ONLY base classes and shims.

AST-based deterministic scan. No utilities, no helper functions.
Guardian hard gate per blueprint: "STRICT IDENTITY ONLY."
"""

from __future__ import annotations

import ast
from pathlib import Path

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
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
        from agentic_core.L0_routing.config.path_constants import (
    """Test no_utility_files_in_base_agents contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    """Test shims_are_pure_reexports contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    """Test no_residual_legacy_decorators_import_in_production contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
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
