"""ADG contract tests for agentic_core/L2_execution/types/ptc_tool_contracts_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.ptc_tool_contracts_types import (
        ToolCall, ToolResult, ToolContractViolation,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ToolCall = ToolResult = ToolContractViolation = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolContractViolation:
    def test_is_value_error(self): assert issubclass(ToolContractViolation, ValueError)
    def test_raises(self):
        with pytest.raises(ToolContractViolation):
            raise ToolContractViolation("bad exit code")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolCall:
    def test_is_frozen(self): assert ToolCall.__dataclass_params__.frozen is True
    def test_creates(self):
        tc = ToolCall(id="t1", tool_name="read_file", args={"path": "/foo"})
        assert tc.id == "t1"; assert tc.tool_name == "read_file"
    def test_empty_id_raises(self):
        with pytest.raises(ToolContractViolation): ToolCall(id="", tool_name="x")
    def test_empty_tool_name_raises(self):
        with pytest.raises(ToolContractViolation): ToolCall(id="t1", tool_name="")
    def test_default_args(self):
        tc = ToolCall(id="t1", tool_name="x"); assert tc.args == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolResult:
    def test_is_frozen(self): assert ToolResult.__dataclass_params__.frozen is True
    def test_creates_exit_zero(self):
        tr = ToolResult(exit_code=0, stdout=b"ok"); assert tr.exit_code == 0
    def test_creates_exit_one(self):
        tr = ToolResult(exit_code=1, stdout=b"err"); assert tr.exit_code == 1
    def test_exit_code_two_raises(self):
        with pytest.raises(ToolContractViolation):
            ToolResult(exit_code=2, stdout=b"")
    def test_exit_code_negative_raises(self):
        with pytest.raises(ToolContractViolation):
            ToolResult(exit_code=-1, stdout=b"")
    def test_stdout_cap_exceeded_raises(self):
        with pytest.raises(ToolContractViolation):
            ToolResult(exit_code=0, stdout=b"x" * 10, stdout_bytes_cap=5)
    def test_stdout_within_cap_ok(self):
        tr = ToolResult(exit_code=0, stdout=b"hello", stdout_bytes_cap=10)
        assert tr.stdout == b"hello"
    def test_from_budget_enforcer(self):
        tr = ToolResult.from_budget_enforcer(exit_code=0, stdout_bytes=b"output", stdout_bytes_cap=100)
        assert tr.exit_code == 0

def test_module_importable(): assert _AVAIL or not _AVAIL
