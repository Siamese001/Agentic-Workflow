"""Smoke tests for crypto_trust_contracts — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.enforcement.crypto_trust_contracts")


def test_module_imports_clean():
    assert mod is not None


def test_HashMismatchTracker_present():
    assert hasattr(mod, "HashMismatchTracker")
    assert isinstance(mod.HashMismatchTracker, type)


def test_hash_artifact_canonical_callable():
    assert callable(mod.hash_artifact_canonical)
