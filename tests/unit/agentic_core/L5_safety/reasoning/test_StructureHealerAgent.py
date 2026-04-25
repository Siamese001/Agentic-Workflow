"""Smoke tests for StructureHealerAgent — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.StructureHealerAgent")


def test_module_imports_clean():
    assert mod is not None


def test_StructureHealingStrategy_class_present():
    assert hasattr(mod, "StructureHealingStrategy")
    assert isinstance(mod.StructureHealingStrategy, type)


def test_StructureHealingType_present():
    assert hasattr(mod, "StructureHealingType")


def test_StructureHealingAction_class_present():
    assert hasattr(mod, "StructureHealingAction")
    assert isinstance(mod.StructureHealingAction, type)
