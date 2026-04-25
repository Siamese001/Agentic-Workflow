"""Smoke tests for SelfUpdatingSafetyEngineAgent — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.SelfUpdatingSafetyEngineAgent")


def test_module_imports_clean():
    assert mod is not None


def test_ThreatLevel_present():
    assert hasattr(mod, "ThreatLevel")


def test_RuleType_present():
    assert hasattr(mod, "RuleType")


def test_SafetyAnalysisMixin_class_present():
    assert hasattr(mod, "SafetyAnalysisMixin")
    assert isinstance(mod.SafetyAnalysisMixin, type)
