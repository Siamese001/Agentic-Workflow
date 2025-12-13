# from archives.legacy_root_folders.infra.sandbox.models import ToolCallRequest  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.infra.sandbox.vm_manager import run_in_ephemeral_vm  # DEPRECATED: Archive import removed to protect archives from validation edits

def test_run_in_ephemeral_vm_basic():
    """TODO: Add docstring."""

    req = ToolCallRequest(tool_name="echo", args=["x"], timeout_s=1.0)
    result = run_in_ephemeral_vm(req, resource_limits={"memory_mb": 64})

    assert result.success is True
    assert result.exit_code == 0
    assert "TOOL echo" in result.stdout
