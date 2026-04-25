"""Smoke tests for StructuralEngineerAgent — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.StructuralEngineerAgent")


def test_module_imports_clean():
    assert mod is not None


def test_StructuralEngineerAgent_class_present():
    assert hasattr(mod, "StructuralEngineerAgent")
    assert isinstance(mod.StructuralEngineerAgent, type)


def test_StructuralEngineerAgent_has_heal_repository():
    assert callable(getattr(mod.StructuralEngineerAgent, "heal_repository", None))
