"""Smoke tests for L3_orchestration types __init__ — wave 31."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.types")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
