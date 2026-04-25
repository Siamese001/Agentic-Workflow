"""Smoke tests for safety_audit_emitter — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.audit.safety_audit_emitter")


def test_module_imports_clean():
    assert mod is not None


def test_SafetyAuditRecord_class_present():
    assert hasattr(mod, "SafetyAuditRecord")
    assert isinstance(mod.SafetyAuditRecord, type)


def test_emit_guardrail_audit_callable():
    assert callable(mod.emit_guardrail_audit)


def test_emit_safety_plane_validation_audit_callable():
    assert callable(mod.emit_safety_plane_validation_audit)
