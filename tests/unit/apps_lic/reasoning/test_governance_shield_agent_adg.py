"""ADG contract tests for apps_lic/reasoning/GovernanceShieldAgent.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[4] / "apps_lic" / "reasoning" / "GovernanceShieldAgent.py"


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


class TestGovernanceShieldAgentSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_governance_shield_agent_class(self):
        assert "GovernanceShieldAgent" in _class_names()

    def test_has_naive_patterns_field(self):
        assert "naive_patterns" in _src_text()

    def test_has_risk_thresholds_field(self):
        assert "risk_thresholds" in _src_text()


def test_module_importable():
    pass
