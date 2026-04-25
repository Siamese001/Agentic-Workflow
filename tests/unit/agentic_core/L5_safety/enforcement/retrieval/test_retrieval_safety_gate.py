"""Smoke tests for retrieval_safety_gate — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.retrieval.retrieval_safety_gate")


def test_module_imports_clean():
    assert mod is not None


def test_RetrievalSafetyGate_present():
    assert hasattr(mod, "RetrievalSafetyGate")
    assert isinstance(mod.RetrievalSafetyGate, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
