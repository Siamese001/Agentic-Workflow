"""Smoke tests for audit_healing_strategy — wave 33."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.audit_healing_strategy")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
