"""
CapabilityRevoker — Token revocation management for L2 execution boundary.

Manages per-trace revocation and authority-version invalidation.
All capability tokens must be validated through this revoker before
any L2 tool invocation is permitted.

Phase 3.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import threading

from agentic_core.L2_execution.enforcement.key_derivation import get_key_version
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


class TokenRevocationError(RuntimeError):
    """Raised when a token is used after revocation."""


class VersionInvalidError(RuntimeError):
    """Raised when a token's authority version is no longer valid."""


class CapabilityRevoker:
    """Thread-safe capability token revocation registry.

    Usage::

        revoker = get_capability_revoker()
        revoker.validate_token(token.trace_id, token.authority_secret_version)
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._revoked_trace_ids: set[str] = set()
        self._invalid_versions: set[str] = set()

    def revoke_token(self, trace_id: str) -> None:
        """Revoke a specific token by its trace ID (immediate effect)."""
        with self._lock:
            self._revoked_trace_ids.add(trace_id)

    def invalidate_version(self, version: str) -> None:
        """Invalidate all tokens carrying a specific authority_secret_version."""
        with self._lock:
            self._invalid_versions.add(version)

    def is_token_revoked(self, trace_id: str) -> bool:
        with self._lock:
            return trace_id in self._revoked_trace_ids

    def is_version_valid(self, version: str) -> bool:
        """Return True iff *version* equals the current key version and is not invalidated."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "CapabilityRevoker.is_version_valid")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:CapabilityRevoker.is_version_valid".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        with self._lock:
            if version in self._invalid_versions:
                return False
        return version == get_key_version()

    def validate_token(self, trace_id: str, authority_secret_version: str) -> None:
        """Raise if token is revoked or version is invalid.

        Args:
            trace_id: The trace_id embedded in the capability token.
            authority_secret_version: The authority_secret_version embedded in the token.

        Raises:
            TokenRevocationError: token has been explicitly revoked.
            VersionInvalidError: token authority version is invalid or rotated away.
        """
        if self.is_token_revoked(trace_id):
            raise TokenRevocationError(f"Capability token revoked: trace_id={trace_id}")
        if not self.is_version_valid(authority_secret_version):
            raise VersionInvalidError(
                f"Capability token authority version invalid: version={authority_secret_version}, current={get_key_version()}"
            )

    def revoked_count(self) -> int:
        with self._lock:
            return len(self._revoked_trace_ids)

    def invalid_version_count(self) -> int:
        with self._lock:
            return len(self._invalid_versions)


_DEFAULT_REVOKER: CapabilityRevoker | None = None
_SINGLETON_LOCK = threading.Lock()


def get_capability_revoker() -> CapabilityRevoker:
    """Return the process-wide CapabilityRevoker singleton."""
    global _DEFAULT_REVOKER
    with _SINGLETON_LOCK:
        if _DEFAULT_REVOKER is None:
            _DEFAULT_REVOKER = CapabilityRevoker()
    return _DEFAULT_REVOKER


def reset_capability_revoker_for_testing() -> None:
    """Reset the singleton (test isolation only)."""
    global _DEFAULT_REVOKER
    with _SINGLETON_LOCK:
        _DEFAULT_REVOKER = None


__all__ = [
    "CapabilityRevoker",
    "TokenRevocationError",
    "VersionInvalidError",
    "get_capability_revoker",
    "reset_capability_revoker_for_testing",
]
