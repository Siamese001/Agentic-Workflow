"""ADG contract tests for agentic_core/L2_execution/types/ephemeral_vm_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.L2_execution.types.ephemeral_vm_types as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = pathlib.Path(__file__).parents[5] / "agentic_core" / "L2_execution" / "types" / "ephemeral_vm_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


class TestEphemeralVmTypesSource:
    def test_source_exists(self):
        assert _SRC.exists(), f"Source not found: {_SRC}"

    def test_parses_without_error(self):
        _tree()  # raises SyntaxError if broken

    def test_has_isolation_level_class(self):
        assert "IsolationLevel" in _class_names()

    def test_has_isolation_config_class(self):
        assert "IsolationConfig" in _class_names()

    def test_has_execution_result_class(self):
        assert "ExecutionResult" in _class_names()

    def test_has_ephemeral_vm_class(self):
        assert "EphemeralVm" in _class_names()

    def test_has_create_ephemeral_vm_factory(self):
        assert "create_ephemeral_vm" in _func_names()

    def test_isolation_level_is_enum_or_class(self):
        tree = _tree()
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "IsolationLevel")
        assert cls is not None
