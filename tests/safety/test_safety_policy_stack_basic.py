import pytest

from stacks_v10_8.safety_policy_stack import SafetyPolicyStack


def _make_stack():
    return SafetyPolicyStack(context=None, debug_mode=False)


def test_safe_text_is_safe():
    stack = _make_stack()
    report = stack.evaluate_text("This is a harmless, generic sentence.")

    assert hasattr(report, "is_safe")
    assert hasattr(report, "findings")
    assert report.is_safe is True
    assert isinstance(report.findings, list)


def test_pii_like_text_triggers_findings():
    stack = _make_stack()
    report = stack.evaluate_text("My social security number is 123-45-6789.")

    assert hasattr(report, "is_safe")
    assert hasattr(report, "findings")
    assert isinstance(report.findings, list)
    assert len(report.findings) >= 1
    assert report.is_safe is False
