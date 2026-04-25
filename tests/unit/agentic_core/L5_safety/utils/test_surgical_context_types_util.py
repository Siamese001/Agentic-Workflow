"""Smoke tests for surgical_context_types_util — wave 29."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.surgical_context_types_util")


def test_module_imports_clean():
    assert mod is not None


def test_ASTCoordinate_class_present():
    assert hasattr(mod, "ASTCoordinate")
    assert isinstance(mod.ASTCoordinate, type)


def test_SurgicalContext_class_present():
    assert hasattr(mod, "SurgicalContext")
    assert isinstance(mod.SurgicalContext, type)
