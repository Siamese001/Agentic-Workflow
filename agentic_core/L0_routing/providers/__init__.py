"""L0 Routing Providers — injectable infrastructure services."""

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_reads_policy_state,
    _emit_snapshots_state,
    _emit_signs_execution_trace,
    emit_replay_key,
    emit_determinism_digest,
)

_emit_records_execution_trace("p0", "evidence", "L0_providers")
_emit_applies_guardrail("p0", "L0_providers", "p0_governance")
_emit_reads_policy_state("p0", "L0_providers", "policy_binding")
_emit_snapshots_state("p0", "L0_providers", "state_snapshot")
emit_replay_key("p0", "L0_providers")
emit_determinism_digest("p0", "L0_providers")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

__all__ = ["ClockProvider"]
