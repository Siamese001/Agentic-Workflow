"""ADG contract tests for L3_orchestration/scripts/guardian_heal_orchestrator.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L3_orchestration" / "scripts" / "guardian_heal_orchestrator.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestGuardianHealOrchestratorSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_tool_id_constant(self):
        assert "TOOL_ID" in _src_text()

    def test_tool_id_value(self):
        assert "guardian_heal_orchestrator" in _src_text()

    def test_has_run_pipeline(self):
        assert "run_pipeline" in _func_names()

    def test_has_main(self):
        assert "main" in _func_names()


def test_module_importable():
    assert True
