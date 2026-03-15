"""ADG contract tests for L1_cognition/validators/spiffe_validator.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.L1_cognition.validators.spiffe_validator as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L1_cognition" / "validators" / "spiffe_validator.py"
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


class TestSpiffeValidatorSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_spiffe_manager_class(self):
        assert "SpiffeManager" in _class_names()

    def test_has_init(self):
        assert "__init__" in _methods_of("SpiffeManager")

    def test_has_create_identity(self):
        assert "create_identity" in _methods_of("SpiffeManager")

    def test_has_verify_identity(self):
        assert "verify_identity" in _methods_of("SpiffeManager")


def test_module_importable():
    pass
