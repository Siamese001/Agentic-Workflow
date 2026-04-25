"""Smoke tests for L4_state.cache __init__ — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.cache")


def test_module_imports_clean():
    assert mod is not None


def test_ConfigFileCache_class_present():
    assert hasattr(mod, "ConfigFileCache")
    assert isinstance(mod.ConfigFileCache, type)


def test_AgentDiscoveryCache_class_present():
    assert hasattr(mod, "AgentDiscoveryCache")
    assert isinstance(mod.AgentDiscoveryCache, type)


def test_NativePersistentCacheClient_class_present():
    assert hasattr(mod, "NativePersistentCacheClient")
    assert isinstance(mod.NativePersistentCacheClient, type)


def test_build_cap_registry_key_callable():
    assert callable(mod.build_cap_registry_key)
