"""Smoke tests for decorators_util — wave 28."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.decorators_util")


def test_module_imports_clean():
    assert mod is not None


def test_standard_heal_callable():
    assert callable(mod.standard_heal)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
