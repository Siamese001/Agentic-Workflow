"""Smoke tests for SurgicalHealingAdapter — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.SurgicalHealingAdapter")


def test_module_imports_clean():
    assert mod is not None


def test_ASTCoordinate_present():
    assert hasattr(mod, "ASTCoordinate")
    assert isinstance(mod.ASTCoordinate, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
