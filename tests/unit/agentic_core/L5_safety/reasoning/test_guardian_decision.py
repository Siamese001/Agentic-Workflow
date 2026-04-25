"""Smoke tests for guardian_decision — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.guardian_decision")


def test_module_imports_clean():
    assert mod is not None


def test_GuardianDecision_class_present():
    assert hasattr(mod, "GuardianDecision")
    assert isinstance(mod.GuardianDecision, type)


def test_GuardianViolationError_is_exception():
    assert issubclass(mod.GuardianViolationError, Exception)


def test_L5Guardian_class_present():
    assert hasattr(mod, "L5Guardian")
    assert isinstance(mod.L5Guardian, type)
