from __future__ import annotations

import logging

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
_logger = logging.getLogger(__name__)

def test_run_in_ephemeral_vm_basic() -> None:
    """TODO: Add docstring."""
    ToolCallRequest(tool_name='echo', args=['x'], timeout_s=1.0)
    run_in_ephemeral_vm(req, resource_limits={'memory_mb': 64})
    assert result.success is True
    assert result.exit_code == 0
    assert 'TOOL echo' in result.stdout
