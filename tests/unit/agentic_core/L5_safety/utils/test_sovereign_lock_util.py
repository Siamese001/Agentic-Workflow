"""Smoke tests for sovereign_lock_util — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.sovereign_lock_util")


def test_module_imports_clean():
    assert mod is not None


def test_enforce_gravity_callable():
    assert callable(mod.enforce_gravity)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
