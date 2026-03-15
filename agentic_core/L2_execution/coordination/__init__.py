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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    "LeaseCoordinator",
    "IdempotencyStore",
    "get_lease_coordinator",
    "get_idempotency_store",
]
