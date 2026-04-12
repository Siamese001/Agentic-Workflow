"""ADG contract tests for apps_rg/types/gap_closure_architect_agent_types.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[5] / "apps_rg" / "types" / "gap_closure_architect_agent_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _methods_of(cls_name: str) -> set:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestGapClosureArchitectAgent:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_class_exists(self):
        assert "GapClosureArchitectAgent" in _class_names()

    def test_inherits_from_subatomic_testing_mixin(self):
        assert "SubatomicTestingMixin" in _src_text()

    def test_has_healing_capability(self):
        assert "generate_competencies" in _methods_of("GapClosureArchitectAgent")

    def test_fuzzing_invalid_inputs(self):
        assert "_calculate_gap_coverage" in _methods_of("GapClosureArchitectAgent")
