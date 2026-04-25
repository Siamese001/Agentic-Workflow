"""Smoke tests for vigilance_seam — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.enforcement.vigilance_seam")


def test_module_imports_clean():
    assert mod is not None


def test_load_vigilance_types_callable():
    assert callable(mod.load_vigilance_types)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
