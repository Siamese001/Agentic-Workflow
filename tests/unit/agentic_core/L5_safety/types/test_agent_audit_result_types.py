"""Smoke tests for agent_audit_result_types — wave 28."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.types.agent_audit_result_types")


def test_module_imports_clean():
    assert mod is not None


def test_AgentAuditResult_class_present():
    assert hasattr(mod, "AgentAuditResult")
    assert isinstance(mod.AgentAuditResult, type)
