"""Smoke tests for layer_gravity_util — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.utils.layer_gravity_util")


def test_module_imports_clean():
    assert mod is not None


def test_extract_layer_from_path_callable():
    assert callable(mod.extract_layer_from_path)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
