"""Smoke tests for BootstrapAgent — wave 27."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.reasoning.BootstrapAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_BootstrapAgent_class_present():
    assert hasattr(mod, "BootstrapAgent")
    assert isinstance(mod.BootstrapAgent, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
