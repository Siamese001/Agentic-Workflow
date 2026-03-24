"""ADG contract tests for agentic_core/L2_execution/types/mcp_client_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.L2_execution.types.mcp_client_types as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = pathlib.Path(__file__).parents[5] / "agentic_core" / "L2_execution" / "types" / "mcp_client_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


class TestMCPClientTypesSource:
    def test_source_exists(self):
        assert _SRC.exists(), f"Source not found: {_SRC}"

    def test_parses_without_error(self):
        _tree()

    def test_has_mcp_client_spec_class(self):
        assert "MCPClientSpec" in _class_names()

    def test_has_mcp_client_stub_class(self):
        assert "MCPClientStub" in _class_names()

    def test_has_mcp_client_registry_class(self):
        assert "MCPClientRegistry" in _class_names()

    def test_has_mcp_client_class(self):
        assert "MCPClient" in _class_names()

    def test_mcp_client_spec_has_validate_method(self):
        tree = _tree()
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "MCPClientSpec")
        method_names = {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}
        assert "validate" in method_names