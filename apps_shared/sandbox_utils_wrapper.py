"""
Sandbox Utils - Thin Wrapper
Delegates to consolidated tools in agentic_core/tools/

This is a backward compatibility shim. All new code should import directly from:
    from agentic_core.tools import *
"""

# Execution operations
import re

from agentic_core.tools.execution import (
    execute_command,
    is_command_allowed,
)

# Filesystem operations now use sandboxed tools
from agentic_core.tools.filesystem import (
    HealingLeaseError,
    PreservationViolationError,
    SandboxViolationError,
    create_directory,
    delete_file,
    list_files,
    move_file,
    read_file,
    validate_sandbox,
    write_file,
)

# Docker sandbox functionality preserved for backward compatibility
from apps_shared.sandbox_utils import DockerSandbox, execute_in_sandbox

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
