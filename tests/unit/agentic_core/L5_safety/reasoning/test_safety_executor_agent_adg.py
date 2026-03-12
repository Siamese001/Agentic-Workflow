"""ADG-driven tests for L5_safety/reasoning/SafetyExecutorAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.SafetyExecutorAgent import (
    BlockReason,
    ExecutionStatus,
    SafetyExecutorAgent,
)


class TestExecutionStatus:
    def test_allowed_member(self):
        assert hasattr(ExecutionStatus, "ALLOWED")

    def test_blocked_member(self):
        assert hasattr(ExecutionStatus, "BLOCKED")

    def test_warned_member(self):
        assert hasattr(ExecutionStatus, "WARNED")

    def test_failed_member(self):
        assert hasattr(ExecutionStatus, "FAILED")


class TestBlockReason:
    def test_safety_violation_member(self):
        assert hasattr(BlockReason, "SAFETY_VIOLATION")

    def test_integrity_failure_member(self):
        assert hasattr(BlockReason, "INTEGRITY_FAILURE")

    def test_permission_denied_member(self):
        assert hasattr(BlockReason, "PERMISSION_DENIED")


class TestSafetyExecutorAgent:
    def test_creates(self):
        agent = SafetyExecutorAgent()
        assert agent is not None

    def test_has_heal_repository(self):
        assert hasattr(SafetyExecutorAgent, "heal_repository")
