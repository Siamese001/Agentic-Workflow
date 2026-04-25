"""Smoke tests for ssot_guardrail — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.ssot_guardrail")


def test_module_imports_clean():
    assert mod is not None


def test_Violation_present():
    assert hasattr(mod, "Violation")
    assert isinstance(mod.Violation, type)


def test_ScanResult_present():
    assert hasattr(mod, "ScanResult")
    assert isinstance(mod.ScanResult, type)
