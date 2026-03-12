"""ADG contract tests for agentic_core/L3_orchestration/types/recursive_orchestration_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L3_orchestration" / "types" / "recursive_orchestration_types.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _top_func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


class TestRecursiveOrchestrationTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_successor_spec(self):
        assert "SuccessorSpec" in _class_names()

    def test_has_recursion_metrics(self):
        assert "RecursionMetrics" in _class_names()

    def test_has_recursive_orchestrator(self):
        assert "RecursiveOrchestrator" in _class_names()

    def test_orchestrator_has_spawn_successor(self):
        tree = _tree()
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "RecursiveOrchestrator")
        methods = {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}
        assert "spawn_successor" in methods

    def test_orchestrator_has_get_metrics(self):
        tree = _tree()
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "RecursiveOrchestrator")
        methods = {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}
        assert "get_metrics" in methods

    def test_has_default_max_depth_constant(self):
        src = _SRC.read_text(encoding="utf-8", errors="replace")
        assert "DEFAULT_MAX_DEPTH" in src
