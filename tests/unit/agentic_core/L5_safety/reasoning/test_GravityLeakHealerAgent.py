"""Smoke tests for GravityLeakHealerAgent — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.GravityLeakHealerAgent")


def test_module_imports_clean():
    assert mod is not None


def test_GravityLeakHealerAgent_in_all():
    assert "GravityLeakHealerAgent" in mod.__all__


def test_GravityLeakHealerAgent_class_present():
    assert hasattr(mod, "GravityLeakHealerAgent")
    assert isinstance(mod.GravityLeakHealerAgent, type)


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"
