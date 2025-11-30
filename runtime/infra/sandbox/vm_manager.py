# VM manager for sandbox operations
from typing import Dict, Any, Optional
from .models import ToolCallRequest, ToolCallResult
from .microvm import create_vm, teardown_vm, exec_in_vm
from .sandbox_errors import SandboxTimeoutError

def run_in_ephemeral_vm(request: ToolCallRequest, resource_limits: Optional[Dict[str, Any]] = None) -> ToolCallResult:
    """Run a tool call in an ephemeral VM with resource limits"""
    if request.timeout_s <= 0:
        raise SandboxTimeoutError("Timeout must be positive")
    
    # Create VM with resource limits
    vm_config = {
        "cpu_ms": 1000,
        "memory_mb": 64,
        "timeout_s": request.timeout_s
    }
    
    if resource_limits:
        vm_config.update(resource_limits)
    
    vm = create_vm(vm_config)
    
    try:
        # Execute the tool call
        result = exec_in_vm(vm, request)
        return result
    finally:
        # Always cleanup the VM
        teardown_vm(vm)
