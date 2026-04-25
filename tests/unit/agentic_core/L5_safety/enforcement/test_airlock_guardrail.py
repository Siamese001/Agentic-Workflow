"""Smoke tests for airlock_guardrail — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.airlock_guardrail")


def test_module_imports_clean():
    assert mod is not None


def test_AirlockProtocol_present():
    assert hasattr(mod, "AirlockProtocol")
    assert isinstance(mod.AirlockProtocol, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
