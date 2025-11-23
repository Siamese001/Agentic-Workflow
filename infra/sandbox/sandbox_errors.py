from __future__ import annotations


class SandboxError(RuntimeError):
    """Base class for sandbox-related errors."""


class SandboxTimeoutError(SandboxError):
    """Raised when a tool call exceeds its allowed timeout inside the VM."""


class SandboxExecutionError(SandboxError):
    """Raised when a tool execution fails inside the VM."""


class SandboxIsolationError(SandboxError):
    """Raised when an isolation invariant appears to be violated."""
