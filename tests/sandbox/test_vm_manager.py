from infrastructure.sandbox.models import ToolCallRequest
from infrastructure.sandbox.vm_manager import run_in_ephemeral_vm


def test_run_in_ephemeral_vm_basic():
    req = ToolCallRequest(tool_name="echo", args=["x"], timeout_s=1.0)
    result = run_in_ephemeral_vm(req, resource_limits={"memory_mb": 64})

    assert result.success is True
    assert result.exit_code == 0
    assert "TOOL echo" in result.stdout






