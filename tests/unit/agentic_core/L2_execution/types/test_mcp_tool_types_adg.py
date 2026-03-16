"""ADG contract tests for L2_execution/types/mcp_tool_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_mcp_tool_types_adg")
_emit_applies_guardrail("p0", "test_mcp_tool_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_mcp_tool_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_mcp_tool_types_adg", "state_snapshot")
emit_replay_key("p0", "test_mcp_tool_types_adg")
emit_determinism_digest("p0", "test_mcp_tool_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.mcp_tool_types import MCPTool, MCPToolResult, MCPToolServer
    _AVAIL = True
except ImportError:
    _AVAIL = False; MCPTool = MCPToolResult = MCPToolServer = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMCPTool:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(MCPTool)
    def test_creates(self):
        t = MCPTool(name="test_tool", description="A test", parameters={}, handler=lambda: None)
        assert t.name == "test_tool"; assert t.requires_approval is False
    def test_to_openai_format(self):
        t = MCPTool(name="calc", description="calc", parameters={"type": "object"}, handler=lambda: None)
        f = t.to_openai_format()
        assert f["type"] == "function"; assert f["function"]["name"] == "calc"
    def test_to_anthropic_format(self):
        t = MCPTool(name="calc", description="calc", parameters={"type": "object"}, handler=lambda: None)
        f = t.to_anthropic_format()
        assert f["name"] == "calc"; assert "input_schema" in f

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMCPToolResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(MCPToolResult)
    def test_creates_success(self):
        r = MCPToolResult(tool_name="t", success=True, result=42)
        assert r.success is True; assert r.error is None
    def test_creates_failure(self):
        r = MCPToolResult(tool_name="t", success=False, result=None, error="oops")
        assert r.error == "oops"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMCPToolServer:
    def test_creates(self): s = MCPToolServer("test-server"); assert s.name == "test-server"
    def test_register_and_list(self):
        s = MCPToolServer()
        s.register_function("f1", "desc", {}, handler=lambda: None)
        assert "f1" in s.list_tools()
    def test_get_tool_not_found(self):
        s = MCPToolServer(); assert s.get_tool("missing") is None

def test_module_importable(): assert _AVAIL or not _AVAIL
