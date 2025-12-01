from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict

from observability import record_event

from infra.sandbox.models import ToolCallRequest, ToolCallResult
from infra.sandbox.sandbox_errors import SandboxTimeoutError


@dataclass
class MicroVM:
    """Lightweight handle representing a sandboxed microVM instance.

    This is a deterministic stub; no real virtualization is performed.
    """

    id: str
    resource_limits: Dict[str, Any]
    created_at_ms: int


def create_vm(resource_limits: Dict[str, Any] | None = None) -> MicroVM:
    vm = MicroVM(id=str(uuid.uuid4()), resource_limits=dict(resource_limits or {}), created_at_ms=_now_ms())
    record_event(
        "sandbox_start",
        {"vm_id": vm.id, "resource_limits": vm.resource_limits},
    )
    return vm


def teardown_vm(vm: MicroVM) -> None:
    record_event(
        "sandbox_stop",
        {"vm_id": vm.id, "uptime_ms": _now_ms() - vm.created_at_ms},
    )


def exec_in_vm(vm: MicroVM, request: ToolCallRequest) -> ToolCallResult:
    """Execute a tool call inside the microVM.

    This implementation is deterministic and does not run arbitrary
    code. It simulates execution and supports basic timeout behavior.
    """

    start_ms = _now_ms()  # noqa: F841 - timestamp for potential debugging
    if request.timeout_s <= 0:
        record_event(
            "sandbox_timeout",
            {"vm_id": vm.id, "tool_name": request.tool_name, "timeout_s": request.timeout_s},
        )
        raise SandboxTimeoutError(f"Tool '{request.tool_name}' timed out before start")

    # Simulate some work based on the number of args.
    simulated_duration_ms = min(50 * len(request.args), int(request.timeout_s * 1000))

    stdout = f"TOOL {request.tool_name} ARGS {request.args}"
    stderr = ""
    exit_code = 0

    duration_ms = simulated_duration_ms
    result = ToolCallResult(
        success=True,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        resource_usage={"cpu_ms": duration_ms, "memory_mb": request.resource_limits.get("memory_mb", 0)},
        duration_ms=duration_ms,
    )

    record_event(
        "sandbox_tool_complete",
        {
            "vm_id": vm.id,
            "tool_name": request.tool_name,
            "success": result.success,
            "exit_code": result.exit_code,
            "duration_ms": result.duration_ms,
        },
    )

    return result


def _now_ms() -> int:
    return int(time.time() * 1000)



