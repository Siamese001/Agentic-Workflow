"""Smoke tests for meta_learning_integration — wave 32."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.meta_learning_integration")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
