"""Smoke tests for sub_atomic_engine_impl — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.reasoning.engines.sub_atomic_engine_impl")


def test_module_imports_clean():
    assert mod is not None


def test_SubAtomicEngineImpl_class_present():
    assert hasattr(mod, "SubAtomicEngineImpl")
    assert isinstance(mod.SubAtomicEngineImpl, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
