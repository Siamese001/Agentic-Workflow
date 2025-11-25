from infrastructure.sandbox.models import ToolCallRequest, ToolCallResult, SandboxEvent


def test_tool_call_request_defaults():
    req = ToolCallRequest(tool_name="echo")
    assert req.tool_name == "echo"
    assert req.args == []
    assert isinstance(req.env, dict)
    assert req.timeout_s > 0


def test_tool_call_result_defaults():
    res = ToolCallResult(success=True)
    assert res.success is True
    assert res.exit_code == 0


def test_sandbox_event_structure():
    evt = SandboxEvent(name="sandbox_start", ts_ms=1234, vm_id="vm1", tool_name=None)
    assert evt.name == "sandbox_start"
    assert evt.ts_ms == 1234
    assert evt.vm_id == "vm1"






