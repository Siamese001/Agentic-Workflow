"""Smoke tests for airlock_trimmer_enforcer — wave 21."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.airlock_trimmer_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_trim_airlock_callable():
    assert callable(mod.trim_airlock)


def test_trim_all_airlocks_callable():
    assert callable(mod.trim_all_airlocks)
