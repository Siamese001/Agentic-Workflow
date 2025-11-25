import pytest

from infrastructure.sandbox.models import ToolCallRequest
from infrastructure.sandbox.vm_manager import run_in_ephemeral_vm
from infrastructure.sandbox.sandbox_errors import SandboxTimeoutError


def test_timeout_error_when_timeout_non_positive():
    req = ToolCallRequest(tool_name="echo", args=[], timeout_s=0.0)
    with pytest.raises(SandboxTimeoutError):
        run_in_ephemeral_vm(req, resource_limits={})






