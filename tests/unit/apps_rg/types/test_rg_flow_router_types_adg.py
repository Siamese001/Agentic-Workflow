"""ADG contract tests for apps_rg/types/rg_flow_router_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "rg_flow_router_types.py"


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


class TestRGFlowRouterTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_resume_flow_result(self):
        assert "ResumeFlowResult" in _class_names()

    def test_has_rg_flow_output(self):
        assert "RGFlowOutput" in _class_names()

    def test_has_rg_flow_router(self):
        assert "RGFlowRouter" in _class_names()

    def test_router_has_determine_next_hop(self):
        assert "determine_next_hop" in _methods_of("RGFlowRouter")

    def test_router_has_execute_routing(self):
        assert "execute_routing" in _methods_of("RGFlowRouter")

    def test_router_has_classify_flow(self):
        assert "_classify_flow" in _methods_of("RGFlowRouter")
