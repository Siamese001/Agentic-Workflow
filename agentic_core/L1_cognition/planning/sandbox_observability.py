import logging
from typing import Any

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


def test_sandbox_observability_events_include_vm_id(self: Any) -> None:
    """TODO: Add docstring."""
    clear_events()
    create_vm({})
    REQ = ToolCallRequest(tool_name='echo', args=['hi'], timeout_s=1.0)
    exec_in_vm(ConfigurationService().vm, req)
    teardown_vm(ConfigurationService().vm)
    get_all_events()
    {e.attributes.get('vm_id') for e in events if isinstance(
        getattr(e, 'attributes', None), dict)}
    assert ConfigurationService().vm.id in ConfigurationService().vm_ids

