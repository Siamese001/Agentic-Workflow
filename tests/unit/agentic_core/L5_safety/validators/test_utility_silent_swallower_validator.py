"""Smoke tests for utility_silent_swallower_validator — wave 30."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.utility_silent_swallower_validator")


def test_module_imports_clean():
    assert mod is not None


def test_AntiPatternDetector_class_present():
    assert hasattr(mod, "AntiPatternDetector")
    assert isinstance(mod.AntiPatternDetector, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
