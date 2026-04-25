"""Smoke tests for chaos_healing_integration_types — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.chaos_healing_integration_types")


def test_module_imports_clean():
    assert mod is not None


def test_HealingStrategyProtocol_present():
    assert hasattr(mod, "HealingStrategyProtocol")


def test_ChaosResilienceStrategy_present():
    assert hasattr(mod, "ChaosResilienceStrategy")
    assert isinstance(mod.ChaosResilienceStrategy, type)


def test_get_chaos_strategy_callable():
    assert callable(mod.get_chaos_strategy)


def test_register_chaos_healing_callable():
    assert callable(mod.register_chaos_healing)
