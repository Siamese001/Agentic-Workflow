"""Smoke tests for escalation_orchestrator — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.escalation.escalation_orchestrator")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_context_types_present():
    for cls_name in ("SafetyContext", "GovernedAction", "TraceContext"):
        assert hasattr(mod, cls_name), f"{cls_name} missing"


def test_HumanEscalationError_is_exception():
    assert issubclass(mod.HumanEscalationError, Exception)


def test_escalate_for_human_review_callable():
    assert callable(mod.escalate_for_human_review)


def test_record_reviewer_outcome_callable():
    assert callable(mod.record_reviewer_outcome)


def test_execute_override_callable():
    assert callable(mod.execute_override)


def test_query_human_escalation_callable():
    assert callable(mod.query_human_escalation)
