"""Smoke tests for guardian_registry_types — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.types.guardian_registry_types")


def test_module_imports_clean():
    assert mod is not None


def test_GuardianTier_enum_present():
    import enum

    assert hasattr(mod, "GuardianTier")
    assert issubclass(mod.GuardianTier, enum.Enum)


def test_GuardianSpec_present():
    assert hasattr(mod, "GuardianSpec")
    assert isinstance(mod.GuardianSpec, type)
