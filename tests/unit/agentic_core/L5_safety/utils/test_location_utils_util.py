"""Smoke tests for location_utils_util — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.location_utils_util")


def test_module_imports_clean():
    assert mod is not None


def test_normalize_location_path_callable():
    assert callable(mod.normalize_location_path)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
