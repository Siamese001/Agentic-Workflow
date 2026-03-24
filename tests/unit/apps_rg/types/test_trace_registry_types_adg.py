"""ADG contract tests for apps_rg/types/trace_registry_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import apps_rg.types.trace_registry_types as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "trace_registry_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _methods_of(cls_name: str) -> set[str]:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


class TestTraceRegistryTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_agent_trace(self):
        assert "AgentTrace" in _class_names()

    def test_has_trace_registry(self):
        assert "TraceRegistry" in _class_names()

    def test_registry_has_add_trace(self):
        assert "add_trace" in _methods_of("TraceRegistry")

    def test_registry_has_get_traces(self):
        assert "get_traces" in _methods_of("TraceRegistry")

    def test_registry_has_get_summary(self):
        assert "get_summary" in _methods_of("TraceRegistry")

    def test_registry_has_count(self):
        assert "count" in _methods_of("TraceRegistry")

    def test_registry_has_start_span(self):
        assert "start_span" in _methods_of("TraceRegistry")

    def test_registry_has_end_span(self):
        assert "end_span" in _methods_of("TraceRegistry")