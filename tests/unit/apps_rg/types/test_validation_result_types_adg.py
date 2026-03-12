"""ADG contract tests for apps_rg/types/validation_result_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit
try:
    import apps_rg.types.validation_result_types as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "validation_result_types.py"


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


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestValidationResultTypesRGSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_validation_result(self):
        assert "ValidationResult" in _class_names()

    def test_has_section_integrator_config(self):
        assert "SectionIntegratorConfig" in _class_names()

    def test_has_section_integrator_result(self):
        assert "SectionIntegratorResult" in _class_names()

    def test_has_section_scope_integrator(self):
        assert "SectionScopeIntegrator" in _class_names()

    def test_integrator_has_generate_overview(self):
        assert "generate_overview" in _methods_of("SectionScopeIntegrator")

    def test_integrator_has_validate_deduplication(self):
        assert "_validate_deduplication" in _methods_of("SectionScopeIntegrator")
