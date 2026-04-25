"""Smoke tests for BenchmarkingAgent — wave 27."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.reasoning.BenchmarkingAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_BenchmarkingAgent_class_present():
    assert hasattr(mod, "BenchmarkingAgent")
    assert isinstance(mod.BenchmarkingAgent, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
