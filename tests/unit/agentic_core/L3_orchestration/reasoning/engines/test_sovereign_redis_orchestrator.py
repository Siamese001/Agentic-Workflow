"""Smoke tests for sovereign_redis_orchestrator — wave 30."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.reasoning.engines.sovereign_redis_orchestrator")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
