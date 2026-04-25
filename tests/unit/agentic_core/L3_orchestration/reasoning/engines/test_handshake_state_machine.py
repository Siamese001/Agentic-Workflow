"""Smoke tests for handshake_state_machine — wave 30."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.reasoning.engines.handshake_state_machine")


def test_module_imports_clean():
    assert mod is not None


def test_HandshakeState_class_present():
    assert hasattr(mod, "HandshakeState")
    assert isinstance(mod.HandshakeState, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
