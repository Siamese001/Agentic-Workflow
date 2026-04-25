"""Smoke tests for runtime_state_guard — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.utils.memory.runtime_state_guard")


def test_module_imports_clean():
    assert mod is not None


def test_RuntimeStateGuard_class_present():
    assert hasattr(mod, "RuntimeStateGuard")
    assert isinstance(mod.RuntimeStateGuard, type)


def test_RuntimeStateGuard_instantiable(tmp_path):
    guard = mod.RuntimeStateGuard(project_root=tmp_path)
    assert guard is not None


def test_RuntimeStateGuard_has_metric_methods():
    cls = mod.RuntimeStateGuard
    assert callable(getattr(cls, "get_metric", None))
    assert callable(getattr(cls, "increment_metric", None))
