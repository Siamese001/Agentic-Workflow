"""ADG contract tests for apps_lic/types/app_content_validator_agent_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import apps_lic.types.app_content_validator_agent_types as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[4]
    / "apps_lic" / "types" / "app_content_validator_agent_types.py"
)


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


class TestAppContentValidatorAgentTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_content_violation_type(self):
        assert "ContentViolationType" in _class_names()

    def test_has_content_violation(self):
        assert "ContentViolation" in _class_names()

    def test_has_content_validation_report(self):
        assert "ContentValidationReport" in _class_names()

    def test_has_content_config(self):
        assert "ContentConfig" in _class_names()

    def test_has_app_content_validator_agent(self):
        assert "AppContentValidatorAgent" in _class_names()

    def test_report_has_has_errors(self):
        assert "has_errors" in _methods_of("ContentValidationReport")

    def test_report_has_pass_rate(self):
        assert "pass_rate" in _methods_of("ContentValidationReport")

    def test_agent_has_validate_email(self):
        assert "validate_email" in _methods_of("AppContentValidatorAgent")

    def test_agent_has_validate_content_cleanliness(self):
        assert "validate_content_cleanliness" in _methods_of("AppContentValidatorAgent")
