# from archives.legacy_root_folders.infra.sandbox.microvm import create_vm, teardown_vm, exec_in_vm  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.infra.sandbox.models import ToolCallRequest  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.observability import clear_events, get_all_events  # INVALID: Cannot import from path with hyphens

def test_sandbox_observability_events_include_vm_id(self) -> None:
    """TODO: Add docstring."""

    clear_events()

    vm = create_vm({})
    req = ToolCallRequest(tool_name="echo", args=["hi"], timeout_s=1.0)
    exec_in_vm(vm, req)
    teardown_vm(vm)

    events = get_all_events()
    vm_ids = {e.attributes.get("vm_id") for e in events if isinstance(getattr(e,
        "attributes",
        None),
        dict)}
    # Some events may not carry vm_id; ensure at least one does.
    assert vm.id in vm_ids
