"""Risk correlation types for deterministic multi-signal correlation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "types", "p0_governance")
_emit_reads_policy_state("p0", "types", "policy_binding")
_emit_snapshots_state("p0", "types", "state_snapshot")
emit_replay_key("p0", "types")
emit_determinism_digest("p0", "types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "types", "execution_auth")
_emit_validates_capability("p2", "types", "capability_check")
_emit_routes_to_capability("p2", "types", "capability_route")
_emit_writes_via_uwg("p2", "types", "uwg_write")
_emit_blocks_direct_write("p2", "types", "direct_write_block")
_emit_records_tool_invocation("p2", "types", "tool_invocation")
_emit_captures_execution_output("p2", "types", "exec_output")
_emit_dispatches_agent("p3", "types", "agent_dispatch")
_emit_coordinates_agents("p3", "types", "agent_coordination")
_emit_records_workflow_lineage("p3", "types", "workflow_lineage")
_emit_records_healing_outcome("p3", "types", "healing_outcome")
_emit_escalates_failure("p3", "types", "failure_escalation")
_emit_orchestrates_workflow("p3", "types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "types", "healing_dispatch")
_emit_invokes_evaluation("p3", "types", "evaluation_signal")
_emit_records_telemetry_event("p4", "types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "types", "eval_metric")
_emit_stores_embedding("p4", "types", "embedding_store")
_emit_updates_meta_learning_state("p4", "types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "types", "exec_snapshot_link")


@dataclass(frozen=True)
class DriftEvent:
    """A drift event for correlation analysis."""

    policy_id: str
    drift_type: str
    severity: float


@dataclass(frozen=True)
class CorrelatedRow:
    """A single correlation row between a fingerprint and a drift event."""

    fingerprint: str
    policy_id: str
    drift_type: str
    severity: float


@dataclass(frozen=True)
class CorrelatedRiskReport:
    """Deterministic report of correlated risks with canonical fingerprint."""

    rows: list[CorrelatedRow]
    correlation_fingerprint: str
    canonical_bytes: bytes

    @classmethod
    def from_canonical_bytes(cls, rows: list[CorrelatedRow], canonical_bytes: bytes) -> CorrelatedRiskReport:
        """Create report from canonical bytes."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CorrelatedRiskReport.from_canonical_bytes")

        correlation_fingerprint = hashlib.sha256(canonical_bytes).hexdigest()
        return cls(
            rows=rows, correlation_fingerprint=correlation_fingerprint, canonical_bytes=canonical_bytes
        )


__all__ = ["CorrelatedRiskReport", "CorrelatedRow", "DriftEvent"]
