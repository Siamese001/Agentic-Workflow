"""Smoke tests for location_path_util — wave 29."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.location_path_util")


def test_module_imports_clean():
    assert mod is not None


def test_is_path_compliant_callable():
    assert callable(mod.is_path_compliant)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
