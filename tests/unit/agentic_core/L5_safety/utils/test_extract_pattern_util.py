"""Smoke tests for extract_pattern_util — wave 29."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.extract_pattern_util")


def test_module_imports_clean():
    assert mod is not None


def test_extract_class_with_context_callable():
    assert callable(mod.extract_class_with_context)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
