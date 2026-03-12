"""ADG contract tests for apps_rg/types/two_phase_generation_node_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[4]
    / "apps_rg" / "types" / "two_phase_generation_node_types.py"
)


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


class TestTwoPhaseGenerationNodeTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_bullet_generation_output(self):
        assert "BulletGenerationOutput" in _class_names()

    def test_has_overview_synthesis_output(self):
        assert "OverviewSynthesisOutput" in _class_names()

    def test_has_two_phase_generation_node(self):
        assert "TwoPhaseGenerationNode" in _class_names()

    def test_node_has_generate_bullets_phase_a(self):
        assert "generate_bullets_phase_a" in _methods_of("TwoPhaseGenerationNode")

    def test_node_has_synthesize_overview_phase_b(self):
        assert "synthesize_overview_phase_b" in _methods_of("TwoPhaseGenerationNode")
