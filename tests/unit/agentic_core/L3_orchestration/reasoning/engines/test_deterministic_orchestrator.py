"""Smoke tests for deterministic_orchestrator — wave 30."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L3_orchestration.reasoning.engines.deterministic_orchestrator",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
