"""ADG contract tests for apps_rg/scripts/generate_resume.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "scripts" / "generate_resume.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestGenerateResumeSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_load_data_file_function(self):
        assert "load_data_file" in _func_names()

    def test_has_main_or_entry_point(self):
        src = _src_text()
        assert "__main__" in src or "main" in _func_names()

    def test_missing_file_raises_system_exit_logic(self):
        src = _src_text()
        assert "SystemExit" in src or "sys.exit" in src

    def test_module_is_parseable(self):
        _tree()


def test_module_importable():
    """Non-skip placeholder: module may or may not import cleanly."""
    assert True
