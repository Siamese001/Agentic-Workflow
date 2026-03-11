"""
Security utilities - canonical re-export shim.

The implementation lives in agentic_core.L5_safety.utils.subprocess_security_util.
This module re-exports for backward compatibility with callers that use
``from agentic_core.utils.security_util import safe_execute``.
"""

from agentic_core.L5_safety.utils.subprocess_security_util import (  # noqa: F401
    SecurityViolationError,
    safe_execute,
    safe_git_execute,
    safe_popen,
    validate_command_whitelist,
)

__all__ = [
    "SecurityViolationError",
    "safe_execute",
    "safe_git_execute",
    "safe_popen",
    "validate_command_whitelist",
]
