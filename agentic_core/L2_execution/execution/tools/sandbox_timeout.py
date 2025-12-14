import pytest


# from archives.legacy_root_folders.infra.sandbox.models import ToolCallRequest  # DEPRECATED: Ar...
# from archives.legacy_root_folders.infra.sandbox.vm_manager import run_in_ephemeral_vm  # DEPREC...
# from archives.legacy_root_folders.infra.sandbox.sandbox_errors import SandboxTimeoutError  # DE...

def test_timeout_error_when_timeout_non_positive():
    """TODO: Add docstring."""

    req = ToolCallRequest(tool_name="echo", args=[], timeout_s=0.0)
    with pytest.raises(SandboxTimeoutError):
        run_in_ephemeral_vm(req, resource_limits={})
