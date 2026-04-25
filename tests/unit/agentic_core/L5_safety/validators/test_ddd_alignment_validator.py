"""Smoke tests for ddd_alignment_validator — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.ddd_alignment_validator")


def test_module_imports_clean():
    assert mod is not None


def test_check_bounded_contexts_callable():
    assert callable(mod.check_bounded_contexts)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
