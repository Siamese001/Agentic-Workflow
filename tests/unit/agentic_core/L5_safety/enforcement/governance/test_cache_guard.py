"""Smoke tests for cache_guard — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.governance.cache_guard")


def test_module_imports_clean():
    assert mod is not None


def test_is_cache_directory_callable():
    assert callable(mod.is_cache_directory)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
