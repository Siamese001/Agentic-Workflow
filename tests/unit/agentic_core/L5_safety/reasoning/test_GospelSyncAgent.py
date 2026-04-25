"""Smoke tests for GospelSyncAgent — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.GospelSyncAgent")


def test_module_imports_clean():
    assert mod is not None


def test_GospelSyncAgent_class_present():
    assert hasattr(mod, "GospelSyncAgent")
    assert isinstance(mod.GospelSyncAgent, type)


def test_GospelSyncAgent_inherits_L0RoutingBase():
    bases = [c.__name__ for c in mod.GospelSyncAgent.__mro__]
    assert "L0RoutingBase" in bases


def test_GospelSyncAgent_has_heal_repository():
    assert callable(getattr(mod.GospelSyncAgent, "heal_repository", None))


def test_GospelSyncAgent_has_perform_sync_audit():
    assert callable(getattr(mod.GospelSyncAgent, "perform_sync_audit", None))


def test_GospelSyncAgent_has_report_drift():
    assert callable(getattr(mod.GospelSyncAgent, "report_drift", None))


def test_GospelSyncAgent_has_heal():
    assert callable(getattr(mod.GospelSyncAgent, "heal", None))


def test_GospelSyncAgent_heal_returns_dict_on_missing_file():
    agent = mod.GospelSyncAgent.__new__(mod.GospelSyncAgent)
    result = agent.heal({"type": "heresy", "file": None})
    assert isinstance(result, dict)
    assert "status" in result
