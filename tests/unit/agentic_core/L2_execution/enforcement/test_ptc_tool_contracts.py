"""Tests for PTC ToolCall and ToolResult contract enforcement.

Phase 4: PTC ToolTranscript STDOUT-only verification.
Spec: Contract [3] PTC Tool Contracts, L2 [STDOUT RULE], Guarantee #24.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.ptc_tool_contracts import (
    ToolCall,
    ToolContractViolation,
    ToolResult,
)


class TestToolCall:
    def test_valid_tool_call(self):
        tc = ToolCall(id="call-001", tool_name="file_system.read", args={"path": "/tmp/x"})
        assert tc.id == "call-001"
        assert tc.tool_name == "file_system.read"

    def test_empty_id_raises(self):
        with pytest.raises(ToolContractViolation, match="id must be non-empty"):
            ToolCall(id="", tool_name="file_system.read")

    def test_empty_tool_name_raises(self):
        with pytest.raises(ToolContractViolation, match="tool_name must be non-empty"):
            ToolCall(id="call-001", tool_name="")


class TestToolResult:
    def test_exit_code_zero_succeeds(self):
        r = ToolResult(exit_code=0, stdout=b"output")
        assert r.exit_code == 0
        assert r.stdout == b"output"

    def test_exit_code_one_succeeds(self):
        r = ToolResult(exit_code=1, stdout=b"error output")
        assert r.exit_code == 1

    def test_exit_code_two_raises(self):
        with pytest.raises(ToolContractViolation, match="exit_code must be 0 or 1"):
            ToolResult(exit_code=2, stdout=b"")

    def test_exit_code_negative_raises(self):
        with pytest.raises(ToolContractViolation, match="exit_code must be 0 or 1"):
            ToolResult(exit_code=-1, stdout=b"")

    def test_exit_code_255_raises(self):
        with pytest.raises(ToolContractViolation, match="exit_code must be 0 or 1"):
            ToolResult(exit_code=255, stdout=b"")

    def test_stdout_within_cap_succeeds(self):
        r = ToolResult(exit_code=0, stdout=b"hello", stdout_bytes_cap=100)
        assert len(r.stdout) <= 100

    def test_stdout_over_cap_raises(self):
        with pytest.raises(ToolContractViolation, match="exceeds cap"):
            ToolResult(exit_code=0, stdout=b"x" * 200, stdout_bytes_cap=100)

    def test_stdout_exact_cap_succeeds(self):
        r = ToolResult(exit_code=0, stdout=b"x" * 100, stdout_bytes_cap=100)
        assert len(r.stdout) == 100

    def test_zero_cap_disables_cap_check(self):
        # cap=0 means no cap enforced
        r = ToolResult(exit_code=0, stdout=b"x" * 10000, stdout_bytes_cap=0)
        assert len(r.stdout) == 10000


class TestToolResultFromBudgetEnforcer:
    def test_valid_construction(self):
        r = ToolResult.from_budget_enforcer(exit_code=0, stdout_bytes=b"output", stdout_bytes_cap=1024)
        assert r.exit_code == 0
        assert r.stdout == b"output"

    def test_invalid_exit_code_raises(self):
        with pytest.raises(ToolContractViolation, match="exit_code must be 0 or 1"):
            ToolResult.from_budget_enforcer(exit_code=2, stdout_bytes=b"", stdout_bytes_cap=1024)

    def test_stdout_over_cap_raises(self):
        with pytest.raises(ToolContractViolation, match="exceeds cap"):
            ToolResult.from_budget_enforcer(exit_code=0, stdout_bytes=b"x" * 500, stdout_bytes_cap=10)

    def test_stdout_at_cap_succeeds(self):
        r = ToolResult.from_budget_enforcer(exit_code=0, stdout_bytes=b"x" * 10, stdout_bytes_cap=10)
        assert len(r.stdout) == 10
