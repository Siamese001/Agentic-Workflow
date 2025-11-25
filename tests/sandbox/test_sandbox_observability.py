from infrastructure.sandbox.microvm import create_vm, teardown_vm, exec_in_vm
from infrastructure.sandbox.models import ToolCallRequest
from observability import clear_events, get_all_events


def test_sandbox_observability_events_include_vm_id():
    clear_events()

    vm = create_vm({})
    req = ToolCallRequest(tool_name="echo", args=["hi"], timeout_s=1.0)
    exec_in_vm(vm, req)
    teardown_vm(vm)

    events = get_all_events()
    vm_ids = {e.attributes.get("vm_id") for e in events if isinstance(getattr(e, "attributes", None), dict)}
    # Some events may not carry vm_id; ensure at least one does.
    assert vm.id in vm_ids






