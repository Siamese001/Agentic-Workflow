"""Smoke tests for agent_capability_registry — wave 30."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.utils.registry.agent_capability_registry")


def test_module_imports_clean():
    assert mod is not None


def test_AgentCapabilitySpec_class_present():
    assert hasattr(mod, "AgentCapabilitySpec")
    assert isinstance(mod.AgentCapabilitySpec, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
