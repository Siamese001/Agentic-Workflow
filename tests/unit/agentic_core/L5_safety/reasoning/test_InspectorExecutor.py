"""Smoke tests for InspectorExecutor — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.InspectorExecutor")


def test_module_imports_clean():
    assert mod is not None


def test_InspectorExecutor_present():
    assert hasattr(mod, "InspectorExecutor")
    assert isinstance(mod.InspectorExecutor, type)


def test_InspectionCapability_present():
    assert hasattr(mod, "InspectionCapability")
