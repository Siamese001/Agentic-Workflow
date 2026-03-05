"""L2 Execution — Redis-backed coordination primitives.

Provides lease acquisition / release and idempotency-key recording for
cross-process tool-call deduplication.

L4 remains the sole source of truth.  Redis here is used exclusively for
coordination (mutual exclusion, idempotency) — never for authoritative state.
"""

from agentic_core.L2_execution.coordination.lease_coordinator import (
    IdempotencyStore,
    LeaseCoordinator,
    get_idempotency_store,
    get_lease_coordinator,
)

__all__ = [
    "LeaseCoordinator",
    "IdempotencyStore",
    "get_lease_coordinator",
    "get_idempotency_store",
]
