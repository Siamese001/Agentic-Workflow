"""Smoke tests for mixture_of_experts — wave 32."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.mixture_of_experts")


def test_module_imports_clean():
    assert mod is not None


def test_MixtureOfExperts_class_present():
    assert hasattr(mod, "MixtureOfExperts")
    assert isinstance(mod.MixtureOfExperts, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
