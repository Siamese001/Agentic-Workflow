"""ADG-driven tests for mixins/hitl_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.mixins.hitl_mixin import ApprovalStatus, HITLMixin, RiskLevel


class TestApprovalStatus:
    def test_pending_value(self):
        from agentic_core.mixins.hitl_mixin import ApprovalStatus, HITLMixin, RiskLevel
        assert ApprovalStatus.PENDING.value == "pending"

    def test_approved_value(self):
        assert ApprovalStatus.APPROVED.value == "approved"

    def test_rejected_value(self):
        assert ApprovalStatus.REJECTED.value == "rejected"

    def test_timeout_value(self):
        assert ApprovalStatus.TIMEOUT.value == "timeout"


class TestRiskLevel:
    def test_low_value(self):
        assert RiskLevel.LOW.value == 1

    def test_critical_highest(self):
        assert RiskLevel.CRITICAL.value > RiskLevel.HIGH.value

    def test_all_levels(self):
        for level in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            assert hasattr(RiskLevel, level)


class TestHITLMixin:
    def test_importable(self):
        assert callable(HITLMixin)

    def test_has_create_approval_request(self):
        assert hasattr(HITLMixin, "create_approval_request")

    def test_has_escalate(self):
        assert hasattr(HITLMixin, "escalate")
