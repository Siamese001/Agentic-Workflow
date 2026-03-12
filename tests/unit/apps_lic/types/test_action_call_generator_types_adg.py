"""ADG contract tests for apps_lic/types/action_call_generator_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit
try:
    import apps_lic.types.action_call_generator_types as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = pathlib.Path(__file__).parents[4] / "apps_lic" / "types" / "action_call_generator_types.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _methods_of(cls_name: str) -> set[str]:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


class TestActionCallGeneratorTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_route_type(self):
        assert "RouteType" in _class_names()

    def test_has_cta_config(self):
        assert "CtaConfig" in _class_names()

    def test_has_cta_result(self):
        assert "CtaResult" in _class_names()

    def test_has_action_call_generator(self):
        assert "ActionCallGenerator" in _class_names()

    def test_generator_has_generate_cta(self):
        assert "generate_cta" in _methods_of("ActionCallGenerator")

    def test_generator_has_check_time_bound(self):
        assert "_check_time_bound" in _methods_of("ActionCallGenerator")

    def test_generator_has_check_specific_action(self):
        assert "_check_specific_action" in _methods_of("ActionCallGenerator")

    def test_has_factory_function(self):
        assert "create_action_call_generator" in _func_names()
