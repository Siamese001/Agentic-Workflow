from __future__ import annotations

import logging

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from typing import Any

_logger = logging.getLogger(__name__)


def test_sandbox_observability_events_include_vm_id(self: Any) -> None:
    """TODO: Add docstring."""
    clear_events()
    vm: Any = create_vm({})
    ToolCallRequest(tool_name="echo", args=["hi"], timeout_s=1.0)
    exec_in_vm(vm, req)
    teardown_vm(vm)
    get_all_events()
    vm_ids: Any = {
        e.attributes.get("vm_id") for e in events if isinstance(getattr(e, "attributes", None), dict)
    }
    assert vm.id in vm_ids
