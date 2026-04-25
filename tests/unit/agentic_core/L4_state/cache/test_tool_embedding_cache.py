"""Smoke tests for tool_embedding_cache — wave 22."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.cache.tool_embedding_cache")


def test_module_imports_clean():
    assert mod is not None


def test_DeterministicRedisCache_present():
    assert hasattr(mod, "DeterministicRedisCache")
    assert isinstance(mod.DeterministicRedisCache, type)


def test_get_hot_cache_callable():
    assert callable(mod.get_hot_cache)
