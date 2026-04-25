"""Smoke tests for validate_path_ssot_util — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.validate_path_ssot_util")


def test_module_imports_clean():
    assert mod is not None


def test_should_exclude_path_callable():
    assert callable(mod.should_exclude_path)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
