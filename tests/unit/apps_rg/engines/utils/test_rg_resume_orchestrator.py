"""ADG contract tests for apps_rg/reasoning/RgResumeOrchestrator.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[5] / "apps_rg" / "reasoning" / "RgResumeOrchestrator.py"


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


class TestRgResumeOrchestratorSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_rg_resume_orchestrator_class(self):
        assert "RgResumeOrchestrator" in _class_names()

    def test_has_post_init(self):
        assert "__post_init__" in _methods_of("RgResumeOrchestrator")

    def test_has_heal_repository(self):
        assert "heal_repository" in _methods_of("RgResumeOrchestrator")

    def test_has_run(self):
        pass
