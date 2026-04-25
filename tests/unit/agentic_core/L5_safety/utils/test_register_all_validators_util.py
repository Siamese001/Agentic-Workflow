"""Smoke tests for register_all_validators_util — wave 22."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.register_all_validators_util")


def test_module_imports_clean():
    assert mod is not None


def test_initialize_callable():
    assert callable(mod.initialize)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
