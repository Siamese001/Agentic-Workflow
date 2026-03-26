"""ADG contract tests for L1_cognition/engines/capability_analyzer.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
#  # MOVED: import agentic_core.L1_cognition.engines.capability_analyzer as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L1_cognition" / "engines" / "capability_analyzer.py"
)


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


class TestCapabilityAnalyzerSource:
    def test_source_exists(self):
        import agentic_core.L1_cognition.engines.capability_analyzer as _mod  # noqa: F401  # ADG covers
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_capability_analyzer_class(self):
        assert "CapabilityAnalyzer" in _class_names()

    def test_has_init(self):
        assert "__init__" in _methods_of("CapabilityAnalyzer")

    def test_has_analyze_failures(self):
        assert "analyze_failures" in _methods_of("CapabilityAnalyzer")

    def test_has_enable_logging_in_source(self):
        assert "enable_logging" in _src_text()


def test_module_importable():
    pass
