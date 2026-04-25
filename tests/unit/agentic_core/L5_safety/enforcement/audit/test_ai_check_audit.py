"""Smoke tests for ai_check_audit — wave 33."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.audit.ai_check_audit")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
