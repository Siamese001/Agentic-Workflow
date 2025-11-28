from infra.sandbox.models import ToolCallRequest
from infra.sandbox.vm_manager import run_in_ephemeral_vm


def test_tool_like_call_runs_in_vm_boundary():
    # In this codebase tools are not first-class, but this test ensures
    # that the sandbox entrypoint can be used as a tool middleware shim.
    req = ToolCallRequest(tool_name="echo", args=["middleware"], timeout_s=1.0)
    result = run_in_ephemeral_vm(req, resource_limits={"memory_mb": 32})

    assert result.success is True
    assert "middleware" in result.stdout






