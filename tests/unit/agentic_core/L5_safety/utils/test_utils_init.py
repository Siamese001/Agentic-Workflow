"""Smoke tests for L5_safety utils __init__ — wave 28."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils")


def test_module_imports_clean():
    assert mod is not None


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
