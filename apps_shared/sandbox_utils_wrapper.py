"""
Sandbox Utils - Thin Wrapper
Delegates to consolidated tools in agentic_core/tools/

This is a backward compatibility shim. All new code should import directly from:
    from agentic_core.tools import *
"""

# Docker sandbox functionality preserved for backward compatibility
from apps_shared.sandbox_utils import DockerSandbox, execute_in_sandbox

# Filesystem operations now use sandboxed tools
from agentic_core.tools.filesystem import (
    read_file,
    write_file,
    move_file,
    list_files,
    delete_file,
    create_directory,
    validate_sandbox,
    SandboxViolationError,
    HealingLeaseError,
    PreservationViolationError,
)

# Execution operations
from agentic_core.tools.execution import (
    execute_command,
    is_command_allowed,
)

__all__ = [
    # Docker (preserved)
    "DockerSandbox",
    "execute_in_sandbox",
    # Filesystem (sandboxed)
    "read_file",
    "write_file",
    "move_file",
    "list_files",
    "delete_file",
    "create_directory",
    "validate_sandbox",
    "SandboxViolationError",
    "HealingLeaseError",
    "PreservationViolationError",
    # Execution
    "execute_command",
    "is_command_allowed",
]
