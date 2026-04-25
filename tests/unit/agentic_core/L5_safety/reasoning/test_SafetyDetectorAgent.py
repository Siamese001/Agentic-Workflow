"""Smoke tests for SafetyDetectorAgent — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.SafetyDetectorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_SafetyThreatType_present():
    assert hasattr(mod, "SafetyThreatType")


def test_ThreatSeverity_present():
    assert hasattr(mod, "ThreatSeverity")


def test_SafetyThreat_present():
    assert hasattr(mod, "SafetyThreat")
    assert isinstance(mod.SafetyThreat, type)
