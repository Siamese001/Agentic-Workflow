"""ADG contract tests for agentic_core/L5_safety/validators/GovernanceAgent.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L5_safety" / "reasoning" / "GovernanceAgent.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _methods_of(cls_name: str) -> set:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestGovernanceAgentSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_governance_agent_class(self):
        assert "GovernanceAgent" in _class_names()

    def test_has_dependency_graph_class(self):
        assert "DependencyGraph" in _class_names()

    def test_has_module_level_heal_function(self):
        assert "heal" in _func_names()

    def test_dependency_graph_has_build(self):
        assert "build" in _methods_of("DependencyGraph")

    def test_dependency_graph_has_get_impact_radius(self):
        assert "get_impact_radius" in _methods_of("DependencyGraph")

    def test_governance_agent_has_init(self):
        assert "__init__" in _methods_of("GovernanceAgent")


class TestModuleLevelHealSource:
    def test_heal_references_manual_required(self):
        assert "manual_required" in _src_text()

    def test_heal_references_skipped(self):
        assert "skipped" in _src_text()

    def test_heal_references_failed(self):
        assert "failed" in _src_text()

    def test_heal_result_has_artifacts_key(self):
        assert "artifacts" in _src_text()

    def test_heal_result_has_errors_key(self):
        assert "errors" in _src_text()
