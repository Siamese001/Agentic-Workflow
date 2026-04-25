"""Smoke tests for safety_audit_emitter — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.audit.safety_audit_emitter")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_context_dataclasses_present():
    for cls_name in ("SafetyContext", "DecisionContext", "TraceContext", "HumanReviewContext"):
        assert hasattr(mod, cls_name), f"{cls_name} missing"
        assert isinstance(getattr(mod, cls_name), type)


def test_emit_safety_audit_record_callable():
    assert callable(mod.emit_safety_audit_record)


def test_emit_human_review_audit_callable():
    assert callable(mod.emit_human_review_audit)


def test_query_safety_audits_callable():
    assert callable(mod.query_safety_audits)


def test_emit_guardrail_audit_callable():
    assert callable(mod.emit_guardrail_audit)


def test_safety_audit_emitted_callable():
    assert callable(mod.safety_audit_emitted)
