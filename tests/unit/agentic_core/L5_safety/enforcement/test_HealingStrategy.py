"""Smoke tests for HealingStrategy — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.HealingStrategy")


def test_module_imports_clean():
    assert mod is not None


def test_HealingStrategy_in_all():
    assert "HealingStrategy" in mod.__all__


def test_HealingStrategy_class_present():
    assert hasattr(mod, "HealingStrategy")
    assert isinstance(mod.HealingStrategy, type)


def test_HealingStrategy_has_execute_agent():
    assert callable(getattr(mod.HealingStrategy, "execute_agent", None))


def test_HealingStrategy_has_load_agent():
    assert callable(getattr(mod.HealingStrategy, "_load_agent", None))


def test_HealingStrategy_has_normalize_result():
    assert callable(getattr(mod.HealingStrategy, "_normalize_result", None))


def test_HealingStrategy_has_should_abort_tier():
    assert callable(getattr(mod.HealingStrategy, "should_abort_tier", None))


def test_HealingStrategy_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_HealingStrategy_should_abort_tier_no_failure_returns_false(tmp_path):
    strategy = mod.HealingStrategy(project_root=str(tmp_path))
    result = strategy.should_abort_tier("Tier 2", [{"status": "PASS"}], execute=False)
    assert result is False


def test_HealingStrategy_should_abort_tier_tier0_failure_returns_true(tmp_path):
    strategy = mod.HealingStrategy(project_root=str(tmp_path))
    result = strategy.should_abort_tier("Tier 0 Pre-Flight", [{"status": "FAIL"}], execute=False)
    assert result is True
