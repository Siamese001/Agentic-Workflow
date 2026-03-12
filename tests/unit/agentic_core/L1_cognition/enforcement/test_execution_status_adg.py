"""ADG-driven tests for L1_cognition/enforcement/execution_status.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.enforcement.execution_status import (
    ExecutionContext,
    ExecutionStatus,
)


class TestExecutionStatus:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionStatus, enum.Enum)

    def test_pending_value(self):
        assert ExecutionStatus.PENDING.value == "pending"

    def test_success_value(self):
        assert ExecutionStatus.SUCCESS.value == "success"

    def test_failed_value(self):
        assert ExecutionStatus.FAILED.value == "failed"


class TestExecutionContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionContext)

    def test_creates_with_defaults(self):
        ctx = ExecutionContext(operation_id="op-123")
        assert ctx.operation_id == "op-123"
        assert ctx.status == ExecutionStatus.PENDING
        assert ctx.start_time is None
        assert ctx.metrics == {}

    def test_creates_with_status(self):
        ctx = ExecutionContext(operation_id="op-1", status=ExecutionStatus.RUNNING)
        assert ctx.status == ExecutionStatus.RUNNING
