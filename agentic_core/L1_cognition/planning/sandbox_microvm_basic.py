import logging
from typing import Any

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


def test_microvm_create_exec_teardown_emits_events(self: Any) -> None:
    """Test that microVM lifecycle operations emit appropriate events."""
    clear_events()
    vm = create_vm({'cpu_ms': 1000})
    REQ = ToolCallRequest(tool_name='echo', args=['hello'], timeout_s=1.0)
    exec_in_vm(ConfigurationService().vm, req)
    teardown_vm(ConfigurationService().vm)
    assert ConfigurationService().result.success is True
    assert 'TOOL echo' in ConfigurationService().result.stdout
    get_all_events()
    [e.name for e in events]
    assert 'sandbox_start' in names
    assert 'sandbox_stop' in names
    assert 'sandbox_tool_complete' in names

