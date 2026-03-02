"""G-16-12: Read-only L4 audit interface for System Learning Meta-Learning Bus.

System Learning may ONLY read from L4 audit surfaces. This module defines:
  - AuditStore: minimal protocol for read-only audit access
  - pull_audit_data(): enforced read-only entry point

Authority invariants are enforced at every call site. Any attempt to write
to audit surfaces raises AuthorityViolation (fail-closed).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    assert_read_only_audit_access,
    assert_zero_execution_authority,
)

# =============================================================================
# AuditStore Protocol
# =============================================================================


@runtime_checkable
class AuditStore(Protocol):
    """Minimal read-only protocol for L4 audit data access.

    Implementors MUST return raw bytes for the requested window.
    Implementors MUST NOT expose any write methods.
    """

    def read_audit_slice(
        self,
        window_start_utc: int,
        window_end_utc: int,
    ) -> bytes:
        """Return raw audit bytes for the given time window.

        Parameters
        ----------
        window_start_utc : int
            Unix timestamp (inclusive) for the start of the window.
        window_end_utc : int
            Unix timestamp (exclusive) for the end of the window.

        Returns
        -------
        bytes
            Raw audit data bytes. May be empty if no data exists.
        """
        ...


# =============================================================================
# pull_audit_data â€” enforced read-only entry point
# =============================================================================


def pull_audit_data(
    store: AuditStore,
    window_start_utc: int,
    window_end_utc: int,
) -> bytes:
    """Pull a read-only audit data slice from the provided store.

    Authority invariants are enforced before any store access:
      - Mode must be READ (not EXECUTE, ACTIVATE, or WRITE).
      - Operation must not be an audit-write operation.

    Parameters
    ----------
    store : AuditStore
        A read-only audit store implementation.
    window_start_utc : int
        Unix timestamp (inclusive) for the start of the window.
    window_end_utc : int
        Unix timestamp (exclusive) for the end of the window.

    Returns
    -------
    bytes
        Raw audit data bytes, exactly as returned by the store (no mutation).

    Raises
    ------
    ValueError
        If window_start_utc >= window_end_utc.
    AuthorityViolation
        If authority invariants are violated (fail-closed).
    """
    # Authority guards â€” fail-closed.
    _ctx = AuthorityContext(
        caller_layer="system_learning.engines.l4_audit_reader",
        operation="read_audit_slice",
        target="l4_audit",
        mode="READ",
    )
    assert_zero_execution_authority(_ctx)
    assert_read_only_audit_access(_ctx)

    # Validate window ordering.
    if window_start_utc >= window_end_utc:
        raise ValueError(f"INVALID_AUDIT_WINDOW: start ({window_start_utc}) must be < end ({window_end_utc})")

    # Delegate to store â€” return bytes exactly as provided (no mutation).
    return store.read_audit_slice(window_start_utc, window_end_utc)
