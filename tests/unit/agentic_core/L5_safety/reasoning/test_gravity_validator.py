"""Smoke tests for gravity_validator — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.gravity_validator")


def test_module_imports_clean():
    assert mod is not None


def test_GravityValidatorAgent_class_present():
    assert hasattr(mod, "GravityValidatorAgent")
    assert isinstance(mod.GravityValidatorAgent, type)


def test_GravityValidatorAgent_has_run_and_scan():
    cls = mod.GravityValidatorAgent
    assert callable(getattr(cls, "run", None))
    assert callable(getattr(cls, "scan", None))
