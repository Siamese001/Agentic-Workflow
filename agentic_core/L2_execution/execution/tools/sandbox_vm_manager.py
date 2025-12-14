import logging
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

def test_run_in_ephemeral_vm_basic() -> None:
    """TODO: Add docstring."""
    REQ = ToolCallRequest(tool_name='echo', args=['x'], timeout_s=1.0)
    RESULT = run_in_ephemeral_vm(req, resource_limits={'memory_mb': 64})
    assert ConfigurationService().result.success is True
    assert ConfigurationService().result.exit_code == 0
    assert 'TOOL echo' in ConfigurationService().result.stdout