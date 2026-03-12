"""ADG contract tests for L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L6_observability" / "dashboards"
    / "verify_dashboard_e2e_playwright_util.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestVerifyDashboardE2ESource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_dashboard_url_constant(self):
        assert "DASHBOARD_URL" in _src_text()

    def test_has_expected_min_rows_constant(self):
        assert "EXPECTED_MIN_ROWS" in _src_text()

    def test_has_port_constant(self):
        assert "PORT" in _src_text()

    def test_has_start_server(self):
        assert "start_server" in _func_names()

    def test_has_main(self):
        assert "main" in _func_names()
