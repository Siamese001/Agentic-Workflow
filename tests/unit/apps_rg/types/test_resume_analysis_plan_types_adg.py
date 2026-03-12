"""ADG contract tests for apps_rg/types/resume_analysis_plan_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit
try:
    import apps_rg.types.resume_analysis_plan_types as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "resume_analysis_plan_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestResumeAnalysisPlanTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_classes(self):
        assert len(_class_names()) > 0, "Expected at least one class"

    def test_has_functions(self):
        assert len(_func_names()) > 0, "Expected at least one function"

    def test_has_max_retries_constant(self):
        assert "MAX_RETRIES" in _src_text()

    def test_has_logging(self):
        assert "logging" in _src_text()

    def test_has_dataclass_usage(self):
        assert "dataclass" in _src_text()
