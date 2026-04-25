"""Smoke tests for DynamicSealAgent — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.DynamicSealAgent")


def test_module_imports_clean():
    assert mod is not None


def test_DynamicSealAgent_class_present():
    assert hasattr(mod, "DynamicSealAgent")
    assert isinstance(mod.DynamicSealAgent, type)


def test_DynamicSealAgent_has_execute_sprint():
    assert callable(getattr(mod.DynamicSealAgent, "execute_sprint", None))


def test_DynamicSealAgent_has_heal():
    assert callable(getattr(mod.DynamicSealAgent, "heal", None))
