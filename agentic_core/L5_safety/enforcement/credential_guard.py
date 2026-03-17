"""Shim — re-exports from security.credential_guard for backward compatibility."""

from agentic_core.L5_safety.enforcement.security.credential_guard import (  # noqa: F401
    CredentialGuard,
    get_credential_guard,
)


class CredentialAccessDeniedError(PermissionError):
    """Raised when credential access is denied by the guard."""


__all__ = ["CredentialAccessDeniedError", "CredentialGuard", "get_credential_guard"]
