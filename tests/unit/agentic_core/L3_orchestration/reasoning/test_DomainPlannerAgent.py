"""Smoke tests for DomainPlannerAgent — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.reasoning.DomainPlannerAgent")


def test_module_imports_clean():
    assert mod is not None


def test_DomainPlannerAgent_class_present():
    assert hasattr(mod, "DomainPlannerAgent")
    assert isinstance(mod.DomainPlannerAgent, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
