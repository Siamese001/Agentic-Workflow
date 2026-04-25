"""Smoke tests for coordination_ledger — wave 19."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.types.coordination_ledger")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0


def test_get_clock_callable():
    assert callable(mod.get_clock)
