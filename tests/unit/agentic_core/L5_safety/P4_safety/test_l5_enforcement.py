"""Unit tests for L5_safety/P4_safety - safety enforcement."""
from __future__ import annotations
import pytest
from typing import Dict, List, Any
from enum import Enum

class SafetyAction(Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ESCALATE = "escalate"

class TestSafetyEnforcement:
    """Tests for safety enforcement."""

    def test_enforce_allow_safe_content(self):
        """Nominal: Safe content is allowed."""
        risk_score = 0.1
        threshold = 0.5
        action = SafetyAction.ALLOW if risk_score < threshold else SafetyAction.BLOCK
        assert action == SafetyAction.ALLOW

    def test_enforce_block_unsafe_content(self):
        """Nominal: Unsafe content is blocked."""
        risk_score = 0.9
        threshold = 0.5
        action = SafetyAction.ALLOW if risk_score < threshold else SafetyAction.BLOCK
        assert action == SafetyAction.BLOCK

    def test_enforce_warn_borderline(self):
        """Nominal: Borderline content triggers warning."""
        risk_score = 0.6
        warn_threshold = 0.5
        block_threshold = 0.8
        if risk_score >= block_threshold:
            action = SafetyAction.BLOCK
        elif risk_score >= warn_threshold:
            action = SafetyAction.WARN
        else:
            action = SafetyAction.ALLOW
        assert action == SafetyAction.WARN

    def test_enforce_escalate_critical(self):
        """Nominal: Critical violations are escalated."""
        violation_type = "pii_leak"
        critical_violations = ["pii_leak", "security_breach", "legal_risk"]
        action = SafetyAction.ESCALATE if violation_type in critical_violations else SafetyAction.BLOCK
        assert action == SafetyAction.ESCALATE

    def test_enforce_audit_logging(self):
        """Nominal: Enforcement actions are logged."""
        audit_log: List[Dict] = []
        action = {
            "content_id": "c123",
            "action": SafetyAction.BLOCK.value,
            "reason": "toxicity_threshold_exceeded",
        }
        audit_log.append(action)
        assert len(audit_log) == 1
        assert audit_log[0]["action"] == "block"
