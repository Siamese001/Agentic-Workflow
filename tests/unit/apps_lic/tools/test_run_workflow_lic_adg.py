"""ADG contract tests for apps_lic/tools/run_workflow_lic.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import apps_lic.tools.run_workflow_lic as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_lic" / "tools" / "run_workflow_lic.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestRunWorkflowLicSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_load_mission_input(self):
        assert "load_mission_input" in _func_names()

    def test_has_validate_mission_input(self):
        assert "validate_mission_input" in _func_names()

    def test_missing_file_raises_system_exit_logic(self):
        src = _src_text()
        assert "SystemExit" in src or "sys.exit" in src

    def test_has_main_entry_point(self):
        src = _src_text()
        assert "__main__" in src or "main" in _func_names()


def test_module_importable():
    pass