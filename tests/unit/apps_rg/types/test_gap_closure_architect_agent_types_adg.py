"""ADG contract tests for apps_rg/types/gap_closure_architect_agent_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "gap_closure_architect_agent_types.py"


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


class TestGapClosureArchitectTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_competency_item(self):
        assert "CompetencyItem" in _class_names()

    def test_has_competencies_output(self):
        assert "CompetenciesOutput" in _class_names()

    def test_has_gap_closure_architect_agent(self):
        assert "GapClosureArchitectAgent" in _class_names()

    def test_agent_has_generate_competencies(self):
        assert "generate_competencies" in _methods_of("GapClosureArchitectAgent")

    def test_agent_has_calculate_gap_coverage(self):
        assert "_calculate_gap_coverage" in _methods_of("GapClosureArchitectAgent")

    def test_agent_has_check_industry_first_ranking(self):
        """Test agent_has_check_industry_first_ranking contract compliance."""
        assert "check_industry_first_ranking" in _methods_of("GapClosureArchitectAgent")
