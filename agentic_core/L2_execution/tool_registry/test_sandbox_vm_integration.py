from __future__ import annotations

import logging

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
_logger = logging.getLogger(__name__)


def test_tool_like_call_runs_in_vm_boundary() -> None:
    """TODO: Add docstring."""
    ToolCallRequest(tool_name="echo", args=["middleware"], timeout_s=1.0)
    run_in_ephemeral_vm(req, resource_limits={"memory_mb": 32})
    assert result.success is True
    assert "middleware" in result.stdout
