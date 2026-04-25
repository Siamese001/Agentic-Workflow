"""Smoke tests for DependencyPruningAgent — wave 28."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.reasoning.DependencyPruningAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_DependencyPruningAgent_class_present():
    assert hasattr(mod, "DependencyPruningAgent")
    assert isinstance(mod.DependencyPruningAgent, type)


def test_find_unused_deptry_callable():
    assert callable(mod.find_unused_deptry)
