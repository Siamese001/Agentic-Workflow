import logging

logger = logging.getLogger(__name__)
# from archives.legacy_root_folders.infra.sandbox.models import ToolCallRequest, ToolCallResult, ...

def test_tool_call_request_defaults():
    """TODO: Add docstring."""

    req = ToolCallRequest(tool_name="echo")
    assert req.tool_name == "echo"
    assert req.args == []
    assert isinstance(req.env, dict)
    assert req.timeout_s > 0

    """TODO: Add docstring."""

def test_tool_call_result_defaults():
    """TODO: Add docstring."""
    res = ToolCallResult(success=True)
    assert res.success is True
    assert res.exit_code == 0
    """TODO: Add docstring."""


def test_sandbox_event_structure():
    """TODO: Add docstring."""
    evt = SandboxEvent(name="sandbox_start", ts_ms=1234, vm_id="vm1", tool_name=None)
    assert evt.name == "sandbox_start"
    assert evt.ts_ms == 1234
    assert evt.vm_id == "vm1"
