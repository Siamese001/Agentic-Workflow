"""ADG contract tests for apps_rg/types/AllProvidersDownError.py (duplicate test file).

Uses AST-based source inspection — immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "AllProvidersDownError.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestAllProvidersDownErrorDetailed:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_exception_class_present(self):
        assert "AllProvidersDownError" in _class_names()

    def test_exception_subclasses_exception(self):
        src = _src_text()
        assert re.search(r"class AllProvidersDownError\s*\(.*Exception.*\)", src)

    def test_hardened_router_present(self):
        assert "HardenedRouter" in _class_names()

    def test_hardened_router_has_reset_circuit_breakers(self):
        tree = _tree()
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "HardenedRouter")
        methods = {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}
        assert "reset_all_circuit_breakers" in methods

    def test_hardened_router_has_provider_health(self):
        tree = _tree()
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "HardenedRouter")
        methods = {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}
        assert "get_provider_health" in methods
