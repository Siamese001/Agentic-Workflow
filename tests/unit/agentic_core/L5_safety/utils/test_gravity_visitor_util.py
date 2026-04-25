"""Smoke tests for gravity_visitor_util — wave 29."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.gravity_visitor_util")


def test_module_imports_clean():
    assert mod is not None


def test_GravityVisitor_class_present():
    assert hasattr(mod, "GravityVisitor")
    assert isinstance(mod.GravityVisitor, type)


def test_get_file_imports_callable():
    assert callable(mod.get_file_imports)
