from __future__ import annotations
import logging
from typing import Any
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
_logger = logging.getLogger(__name__)

def test_run_in_ephemeral_vm_basic() -> None:
    """TODO: Add docstring."""
    REQ: Any = ToolCallRequest(tool_name='echo', args=['x'], timeout_s=1.0)
    RESULT: Any = run_in_ephemeral_vm(req, resource_limits={'memory_mb': 64})
    assert result.success is True
    assert result.exit_code == 0
    assert 'TOOL echo' in result.stdout
