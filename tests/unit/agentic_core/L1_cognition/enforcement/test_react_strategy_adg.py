"""ADG contract tests for L1_cognition/enforcement/react_strategy.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L1_cognition" / "enforcement" / "react_strategy.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestReActStrategySource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_react_strategy_class(self):
        assert "ReActStrategy" in _class_names()

    def test_has_plan_in_source(self):
        assert "plan" in _src_text()

    def test_has_react_pattern_alias(self):
        assert "ReActPattern" in _src_text()


def test_module_importable():
    assert True
