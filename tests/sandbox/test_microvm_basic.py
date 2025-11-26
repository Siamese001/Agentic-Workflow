from infra.sandbox.microvm import create_vm, teardown_vm, exec_in_vm
from infra.sandbox.models import ToolCallRequest
from observability import get_all_events, clear_events


def test_microvm_create_exec_teardown_emits_events():
    clear_events()

    vm = create_vm({"cpu_ms": 1000})
    req = ToolCallRequest(tool_name="echo", args=["hello"], timeout_s=1.0)

    result = exec_in_vm(vm, req)
    teardown_vm(vm)

    assert result.success is True
    assert "TOOL echo" in result.stdout

    events = get_all_events()
    names = [e.name for e in events]
    assert "sandbox_start" in names
    assert "sandbox_stop" in names
    assert "sandbox_tool_complete" in names






