"""Smoke tests for SafetyInspectorAgent — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.SafetyInspectorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_ConstitutionalOverseer_class_present():
    assert hasattr(mod, "ConstitutionalOverseer")
    assert isinstance(mod.ConstitutionalOverseer, type)


def test_ActionRequest_class_present():
    assert hasattr(mod, "ActionRequest")
    assert isinstance(mod.ActionRequest, type)


def test_ViolationCheck_class_present():
    assert hasattr(mod, "ViolationCheck")
    assert isinstance(mod.ViolationCheck, type)
