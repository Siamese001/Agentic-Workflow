import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

def test_tool_like_call_runs_in_vm_boundary() -> None:
    """TODO: Add docstring."""
    REQ = ToolCallRequest(tool_name='echo', args=['middleware'], timeout_s=1.0)
    RESULT = run_in_ephemeral_vm(req, resource_limits={'memory_mb': 32})
    assert ConfigurationService().result.success is True
    assert 'middleware' in ConfigurationService().result.stdout