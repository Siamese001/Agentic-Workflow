from __future__ import annotations

from typing import Any, Dict

from infra.sandbox.microvm import MicroVM, create_vm, teardown_vm, exec_in_vm
from infra.sandbox.models import ToolCallRequest, ToolCallResult


def run_in_ephemeral_vm(request: ToolCallRequest, resource_limits: Dict[str, Any] | None = None) -> ToolCallResult:
    """Convenience helper to run a single tool call in an ephemeral VM.

    This creates a VM, executes the request, and tears the VM down,
    ensuring cleanup even on errors.
    """

    vm = create_vm(resource_limits or {})
    try:
        return exec_in_vm(vm, request)
    finally:
        teardown_vm(vm)
