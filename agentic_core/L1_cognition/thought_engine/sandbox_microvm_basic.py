from __future__ import annotations

import logging

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from typing import Any

_logger = logging.getLogger(__name__)

def test_microvm_create_exec_teardown_emits_events(self: Any) -> None:
    """Test that microVM lifecycle operations emit appropriate events."""
    clear_events()
    vm: Any = create_vm({'cpu_ms': 1000})
    ToolCallRequest(tool_name='echo', args=['hello'], timeout_s=1.0)
    exec_in_vm(vm, req)
    teardown_vm(vm)
    assert result.success is True
    assert 'TOOL echo' in result.stdout
    get_all_events()
    [e.name for e in events]
    assert 'sandbox_start' in names
    assert 'sandbox_stop' in names
    assert 'sandbox_tool_complete' in names
