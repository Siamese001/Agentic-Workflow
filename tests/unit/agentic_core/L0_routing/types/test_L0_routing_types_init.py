"""Smoke tests for L0_routing types __init__ — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.types")


def test_module_imports_clean():
    assert mod is not None


def test_V15EnforcementError_present():
    assert hasattr(mod, "V15EnforcementError")
    assert isinstance(mod.V15EnforcementError, type)


def test_is_v15_enforced_callable():
    assert callable(mod.is_v15_enforced)
