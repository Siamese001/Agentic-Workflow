"""Smoke tests for git_kraken_healing_strategy — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.git_kraken_healing_strategy")


def test_module_imports_clean():
    assert mod is not None


def test_GitKrakenHealingStrategy_present():
    assert hasattr(mod, "GitKrakenHealingStrategy")
    assert isinstance(mod.GitKrakenHealingStrategy, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
