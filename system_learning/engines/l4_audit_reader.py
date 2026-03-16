"""L4 audit reader — read-only access to audit surfaces with authority guards.

System Learning has zero execution authority.  All reads from L4 audit
surfaces are validated through constitutional authority invariants before
the store is consulted.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    AuthorityViolation,  # re-exported for callers
    assert_read_only_audit_access,
    assert_zero_execution_authority,
)

_emit_records_execution_trace("p0", "evidence", "l4_audit_reader")
_emit_applies_guardrail("p0", "l4_audit_reader", "p0_governance")
_emit_reads_policy_state("p0", "l4_audit_reader", "policy_binding")
_emit_snapshots_state("p0", "l4_audit_reader", "state_snapshot")
emit_replay_key("p0", "l4_audit_reader")
emit_determinism_digest("p0", "l4_audit_reader")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# =============================================================================
# AuditStore protocol (read-only)
# =============================================================================


@runtime_checkable
class AuditStore(Protocol):
    """Read-only protocol for L4 audit stores.

    Intentionally exposes NO write, append, delete, or mutate methods.
    """

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        """Return raw audit bytes for the given time window."""
        ...


# =============================================================================
# pull_audit_data
# =============================================================================


def pull_audit_data(
    store: AuditStore,
    window_start_utc: int,
    window_end_utc: int,
) -> bytes:
    """Pull audit data from an AuditStore for a validated time window.

    Parameters
    ----------
    store : AuditStore
        The audit store to read from.
    window_start_utc : int
        Window start (inclusive, Unix timestamp).  Must be strictly less
        than ``window_end_utc``.
    window_end_utc : int
        Window end (exclusive, Unix timestamp).

    Returns
    -------
    bytes
        Raw audit data for the window (may be empty).

    Raises
    ------
    ValueError
        If ``window_start_utc >= window_end_utc``.
    AuthorityViolation
        If the constitutional authority guards reject the operation.
    """
    if window_start_utc >= window_end_utc:
        raise ValueError(
            "INVALID_AUDIT_WINDOW: window_start_utc must be strictly less than window_end_utc"
        )

    ctx = AuthorityContext(
        caller_layer="system_learning.engines.l4_audit_reader",
        operation="read_audit_slice",
        target="l4_audit",
        mode="READ",
    )
    assert_read_only_audit_access(ctx)
    assert_zero_execution_authority(ctx)

    return store.read_audit_slice(window_start_utc, window_end_utc)


__all__ = [
    "AuditStore",
    "AuthorityViolation",
    "pull_audit_data",
]
