
# from archives.legacy_root_folders.infra.sandbox.models import ToolCallRequest  # DEPRECATED: Ar...
# from archives.legacy_root_folders.infra.sandbox.vm_manager import run_in_ephemeral_vm  # DEPREC...

def test_tool_like_call_runs_in_vm_boundary():
    """TODO: Add docstring."""

    # In this codebase tools are not first-class, but this test ensures
    # that the sandbox entrypoint can be used as a tool middleware shim.
    req = ToolCallRequest(tool_name="echo", args=["middleware"], timeout_s=1.0)
    result = run_in_ephemeral_vm(req, resource_limits={"memory_mb": 32})

    assert result.success is True
    assert "middleware" in result.stdout
