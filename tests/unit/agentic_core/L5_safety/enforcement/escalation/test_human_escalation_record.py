"""Smoke tests for human_escalation — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.escalation.human_escalation")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_EscalationTriggerType_enum():
    import enum

    assert issubclass(mod.EscalationTriggerType, enum.Enum)


def test_ReviewerOutcome_enum():
    import enum

    assert issubclass(mod.ReviewerOutcome, enum.Enum)


def test_HumanEscalationError_is_exception():
    assert issubclass(mod.HumanEscalationError, Exception)


def test_HumanEscalationRecord_present():
    assert hasattr(mod, "HumanEscalationRecord")
    assert isinstance(mod.HumanEscalationRecord, type)
