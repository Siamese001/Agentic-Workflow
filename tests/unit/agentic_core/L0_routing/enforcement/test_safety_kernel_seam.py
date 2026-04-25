"""Smoke tests for safety_kernel_seam — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.enforcement.safety_kernel_seam")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0, "safety_kernel_seam must expose at least one public symbol"
