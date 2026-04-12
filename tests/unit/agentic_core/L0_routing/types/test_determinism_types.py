"""ADG contract tests for agentic_core/L0_routing/types/determinism_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[5] / "agentic_core" / "L0_routing" / "types" / "determinism_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


class GeneratedTest:
    """Generated test class for agentic_core.L0_routing.types.determinism_types."""

    def test_FixConstraint_init(self):
        """Test FixConstraint class exists."""
        assert "FixConstraint" in _class_names()

    def test_SurgicalManifest_init(self):
        """Test SurgicalManifest class exists."""
        assert "SurgicalManifest" in _class_names()

    def test_SurgicalManifest_verify_hash(self):
        """Test SurgicalManifest has verify_hash method."""
        # Check method exists in class
        tree = _tree()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "SurgicalManifest":
                methods = {n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)}
                assert "verify_hash" in methods
                return
        pytest.fail("SurgicalManifest class not found")

    def test_validate_semantic_clock(self):
        """Test validate_semantic_clock function exists."""
        assert "validate_semantic_clock" in _func_names()

    def test_verify_hash(self):
        """Test verify_hash function exists."""
        assert "verify_hash" in _func_names()
