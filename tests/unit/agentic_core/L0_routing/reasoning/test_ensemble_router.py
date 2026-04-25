"""Smoke tests for ensemble_router — wave 32."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.ensemble_router")


def test_module_imports_clean():
    assert mod is not None


def test_EnsembleRouter_class_present():
    assert hasattr(mod, "EnsembleRouter")
    assert isinstance(mod.EnsembleRouter, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
