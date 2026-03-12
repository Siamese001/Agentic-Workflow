"""ADG contract tests for agentic_core/L5_safety/types/validation_result_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L5_safety" / "types" / "validation_result_types.py"
)


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


class TestValidationResultTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_validation_result(self):
        assert "ValidationResult" in _class_names()

    def test_has_adaptive_recovery_loop(self):
        assert "AdaptiveRecoveryLoop" in _class_names()

    def test_has_title_composer_config(self):
        assert "TitleComposerConfig" in _class_names()

    def test_has_title_composer_result(self):
        assert "TitleComposerResult" in _class_names()

    def test_adaptive_recovery_loop_has_reset(self):
        assert "reset" in _methods_of("AdaptiveRecoveryLoop")

    def test_adaptive_recovery_loop_has_record_failure(self):
        assert "record_failure" in _methods_of("AdaptiveRecoveryLoop")

    def test_has_executive_title_composer_factory(self):
        assert "create_executive_title_composer" in _func_names() or "executive_title_composer" in _func_names()
