"""Smoke tests for cache_admission_gate — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.utils.memory.cache_admission_gate")


def test_module_imports_clean():
    assert mod is not None


def test_CacheAdmissionDecision_present():
    assert hasattr(mod, "CacheAdmissionDecision")
    assert isinstance(mod.CacheAdmissionDecision, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
