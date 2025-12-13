"""Execution Sandbox for Secure Code Execution.

Phase 3 - Pillar 14: Execution Sandbox (Hardened Ephemeral)
Micro-VM based isolation for secure code execution.
"""

from .firecracker_manager import (
    FirecrackerManager,
    VMConfig,
    VMStatus,
    create_firecracker_manager,
)
from .ephemeral_vm import (
    EphemeralVM,
    ExecutionResult,
    IsolationConfig,
    create_ephemeral_vm,
)

__all__ = [
    "FirecrackerManager",
    "VMConfig",
    "VMStatus",
    "create_firecracker_manager",
    "EphemeralVM",
    "ExecutionResult",
    "IsolationConfig",
    "create_ephemeral_vm",
]
