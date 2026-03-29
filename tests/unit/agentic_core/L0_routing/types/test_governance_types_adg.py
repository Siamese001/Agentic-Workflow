"""ADG contract tests for agentic_core/L0_routing/types/governance_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[5] / "agentic_core" / "L0_routing" / "types" / "governance_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


class GeneratedTest:
    """Generated test class for agentic_core.L0_routing.types.governance_types."""

    def test_is_expired(self):
        """Test is_expired function exists."""
        assert "is_expired" in _func_names()
