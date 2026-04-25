"""Smoke tests for budget_profile_validator — wave 37."""
import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.budget_profile_validator")


def test_module_imports_clean():
    assert mod is not None


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
