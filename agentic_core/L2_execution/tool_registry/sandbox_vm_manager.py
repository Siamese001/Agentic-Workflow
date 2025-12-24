import logging

_logger = logging.getLogger(__name__)
# from archives.legacy_root_folders.infra.sandbox.models import ToolCallRequest  # DEPRECATED: Ar...
# from archives.legacy_root_folders.infra.sandbox.vm_manager import run_in_ephemeral_vm  # DEPREC...


def test_run_in_ephemeral_vm_basic() -> None:
    """TODO: Add docstring."""

    REQ = ToolCallRequest(tool_name="echo", args=["x"], timeout_s=1.0)
    RESULT = run_in_ephemeral_vm(req, resource_limits={"memory_mb": 64})

    assert result.success is True
    assert result.exit_code == 0
    assert "TOOL echo" in result.stdout
