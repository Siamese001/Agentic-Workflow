"""
Structural invariant: agentic_core must NEVER import from ops_scripts.

AST-based deterministic scan. No heuristics. No exceptions.
Guardian hard gate per §28 Layer Boundary Enforcement Lock.
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    OPS_SCRIPTS_DIR,
)

ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = ROOT / AGENTIC_CORE_DIR


def _scan_boundary_violations() -> list[str]:
    """AST scan: find all agentic_core modules importing from ops_scripts."""
    violations: list[str] = []
    for py_file in AGENTIC_CORE.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        rel = py_file.relative_to(ROOT)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name and alias.name.startswith(OPS_SCRIPTS_DIR):
                        violations.append(f"{rel}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(OPS_SCRIPTS_DIR):
                    violations.append(f"{rel}:{node.lineno}: from {node.module} import ...")
    return violations


class TestAgenticCoreOpsScriptsBoundary:
    """Hard gate: agentic_core must not import ops_scripts."""

    def test_no_agentic_core_imports_ops_scripts(self) -> None:
        from agentic_core.L0_routing.config.path_constants import (
    """Test no_agentic_core_imports_ops_scripts contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    """Test synthetic_violation_detected contract compliance."""
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
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(OPS_SCRIPTS_DIR):
                    found = True
        assert found, "Scanner failed to detect synthetic ops_scripts import"
