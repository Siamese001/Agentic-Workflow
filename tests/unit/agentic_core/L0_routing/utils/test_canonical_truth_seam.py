"""Smoke tests for canonical_truth_seam — wave 32."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.utils.canonical_truth_seam")


def test_module_imports_clean():
    assert mod is not None


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
