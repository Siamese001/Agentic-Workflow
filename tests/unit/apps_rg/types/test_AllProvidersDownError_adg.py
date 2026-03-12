"""ADG contract tests for apps_rg/types/AllProvidersDownError.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[4] / "apps_rg" / "types" / "AllProvidersDownError.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestAllProvidersDownErrorSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_all_providers_down_error(self):
        assert "AllProvidersDownError" in _class_names()

    def test_has_hardened_router(self):
        assert "HardenedRouter" in _class_names()

    def test_all_providers_down_error_subclasses_exception(self):
        import re
        src = _src_text()
        assert re.search(r"class AllProvidersDownError\s*\(.*Exception.*\)", src), (
            "AllProvidersDownError must subclass Exception"
        )

    def test_hardened_router_has_get_config(self):
        tree = _tree()
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "HardenedRouter")
        methods = {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}
        assert "get_config" in methods
