"""Smoke tests for dependency_pruning_util — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.dependency_pruning_util")


def test_module_imports_clean():
    assert mod is not None


def test_PruningResult_class_present():
    assert hasattr(mod, "PruningResult")
    assert isinstance(mod.PruningResult, type)


def test_DependencyPruner_class_present():
    assert hasattr(mod, "DependencyPruner")
    assert isinstance(mod.DependencyPruner, type)


def test_safe_execute_callable():
    assert callable(mod.safe_execute)
