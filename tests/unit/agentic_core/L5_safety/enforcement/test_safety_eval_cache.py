"""Smoke tests for safety_eval_cache — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.safety_eval_cache")


def test_module_imports_clean():
    assert mod is not None


def test_DeterministicRedisCache_present():
    assert hasattr(mod, "DeterministicRedisCache")
    assert isinstance(mod.DeterministicRedisCache, type)


def test_get_hot_cache_callable():
    assert callable(mod.get_hot_cache)


def test_build_safety_eval_key_callable():
    assert callable(mod.build_safety_eval_key)
