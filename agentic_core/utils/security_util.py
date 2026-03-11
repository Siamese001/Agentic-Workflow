"""
Security utilities - canonical re-export shim.

The implementation lives in agentic_core.L5_safety.utils.subprocess_security_util.
This module re-exports for backward compatibility with callers that use
``from agentic_core.utils.security_util import safe_execute``.
"""

from agentic_core.L5_safety.utils.subprocess_security_util import (  # noqa: F401
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
