"""Smoke tests for promotion_write_gateway — wave 22."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.enforcement.promotion_write_gateway")


def test_module_imports_clean():
    assert mod is not None


def test_ProofOfLedger_present():
    assert hasattr(mod, "ProofOfLedger")
    assert isinstance(mod.ProofOfLedger, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
