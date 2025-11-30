# Sandbox-specific error classes

class SandboxTimeoutError(Exception):
    """Raised when sandbox operation times out"""
    pass

class SandboxResourceError(Exception):
    """Raised when sandbox resource limits are exceeded"""
    pass

class SandboxSecurityError(Exception):
    """Raised when sandbox security policy is violated"""
    pass
