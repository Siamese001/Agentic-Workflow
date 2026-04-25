"""Smoke tests for TerritoryChangeHandlerAgent — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.TerritoryChangeHandlerAgent")


def test_module_imports_clean():
    assert mod is not None


def test_TerritoryChangeHandlerAgent_class_present():
    assert hasattr(mod, "TerritoryChangeHandlerAgent")
    assert isinstance(mod.TerritoryChangeHandlerAgent, type)
