"""Smoke tests for dependency_healing_integration_types — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.dependency_healing_integration_types")


def test_module_imports_clean():
    assert mod is not None


def test_HealingStrategyProtocol_present():
    assert hasattr(mod, "HealingStrategyProtocol")


def test_DependencyPruningStrategy_present():
    assert hasattr(mod, "DependencyPruningStrategy")
    assert isinstance(mod.DependencyPruningStrategy, type)


def test_get_dependency_strategy_callable():
    assert callable(mod.get_dependency_strategy)


def test_register_dependency_healing_callable():
    assert callable(mod.register_dependency_healing)
