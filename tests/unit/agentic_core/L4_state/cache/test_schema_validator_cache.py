"""Smoke tests for schema_validator_cache — wave 22."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.cache.schema_validator_cache")


def test_module_imports_clean():
    assert mod is not None


def test_DeterministicRedisCache_present():
    assert hasattr(mod, "DeterministicRedisCache")
    assert isinstance(mod.DeterministicRedisCache, type)


def test_get_hot_cache_callable():
    assert callable(mod.get_hot_cache)
