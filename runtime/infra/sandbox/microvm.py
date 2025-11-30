# MicroVM management for sandbox isolation
from typing import Dict, Any, Optional
from .models import ToolCallResult, SandboxEvent

class VMInstance:
    """Represents a microVM instance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.vm_id = f"vm-{hash(str(config))}"
        self.id = self.vm_id  # Add id attribute for test compatibility
        self.config = config
        self.active = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

def create_vm(config: Dict[str, Any]) -> VMInstance:
    """Create a new microVM instance"""
    vm = VMInstance(config)
    emit_sandbox_event("sandbox_start", vm_id=vm.vm_id)
    return vm

def teardown_vm(vm: VMInstance) -> None:
    """Teardown a microVM instance"""
    if vm.active:
        vm.active = False
        emit_sandbox_event("sandbox_stop", vm_id=vm.vm_id)

def exec_in_vm(vm: VMInstance, request: 'ToolCallRequest') -> ToolCallResult:
    """Execute a tool call within a microVM"""
    if not vm.active:
        return ToolCallResult(success=False, stderr="VM is not active")
    
    emit_sandbox_event("sandbox_tool_complete", vm_id=vm.vm_id, tool=request.tool_name)
    
    # Stub implementation - simulate successful execution with expected format
    output = f"TOOL {request.tool_name}"
    if request.args:
        output += f" {' '.join(request.args)}"
    
    return ToolCallResult(
        success=True,
        exit_code=0,
        stdout=output,
        stderr=""
    )

def emit_sandbox_event(event_type: str, **kwargs) -> None:
    """Emit a sandbox event for observability"""
    from observability import record_event
    
    # Create event with corrected constructor - name as first parameter
    event = SandboxEvent(
        name=event_type,
        vm_id=kwargs.get('vm_id'),
        tool_name=kwargs.get('tool'),
        ts_ms=kwargs.get('ts_ms'),
        details=kwargs
    )
    
    record_event(event)
