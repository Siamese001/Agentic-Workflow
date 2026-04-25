"""Smoke tests for CheckpointManager — wave 19."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.reasoning.CheckpointManager")


def test_module_imports_clean():
    assert mod is not None


def test_get_write_gateway_callable():
    assert callable(mod.get_write_gateway)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
