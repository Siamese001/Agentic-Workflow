"""Smoke tests for capacity_snapshot — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.capacity_snapshot")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_CapacityRegistry_present():
    assert hasattr(mod, "CapacityRegistry")
    assert isinstance(mod.CapacityRegistry, type)


def test_get_capacity_registry_callable():
    assert callable(mod.get_capacity_registry)


def test_reset_capacity_registry_callable():
    assert callable(mod.reset_capacity_registry)


def test_singleton_pattern():
    mod.reset_capacity_registry()
    reg1 = mod.get_capacity_registry()
    reg2 = mod.get_capacity_registry()
    assert reg1 is reg2


def test_RouteDegradationState_enum():
    import enum

    assert issubclass(mod.RouteDegradationState, enum.Enum)
    assert hasattr(mod, "HEALTHY")
    assert hasattr(mod, "DEGRADED")
    assert hasattr(mod, "SATURATED")
