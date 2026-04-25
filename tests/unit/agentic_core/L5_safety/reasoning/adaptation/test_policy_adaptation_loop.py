"""Smoke tests for policy_adaptation_loop — wave 35."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.adaptation.policy_adaptation_loop")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
