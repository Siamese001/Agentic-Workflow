"""Smoke tests for chunk_metadata — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.utils.chunk_metadata")


def test_module_imports_clean():
    assert mod is not None


def test_now_utc_iso_callable():
    assert callable(mod.now_utc_iso)


def test_compute_source_sha_callable():
    assert callable(mod.compute_source_sha)


def test_build_canonical_digest_callable():
    assert callable(mod.build_canonical_digest)
