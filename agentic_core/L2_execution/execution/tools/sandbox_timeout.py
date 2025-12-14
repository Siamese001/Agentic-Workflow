import logging
import pytest
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


def test_timeout_error_when_timeout_non_positive() -> None:
    """TODO: Add docstring."""
    REQ = ToolCallRequest(tool_name='echo', args=[], timeout_s=0.0)
    with pytest.raises(SandboxTimeoutError):
        run_in_ephemeral_vm(req, resource_limits={})
