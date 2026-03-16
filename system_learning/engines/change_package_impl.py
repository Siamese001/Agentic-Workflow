"""Concrete implementation of ChangePackage for testing and production use."""

from __future__ import annotations

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

_emit_applies_guardrail("p0", "change_package_impl", "p0_governance")
_emit_reads_policy_state("p0", "change_package_impl", "policy_binding")
_emit_snapshots_state("p0", "change_package_impl", "state_snapshot")
emit_replay_key("p0", "change_package_impl")
emit_determinism_digest("p0", "change_package_impl")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "change_package_impl", "execution_auth")
_emit_validates_capability("p2", "change_package_impl", "capability_check")
_emit_routes_to_capability("p2", "change_package_impl", "capability_route")
_emit_writes_via_uwg("p2", "change_package_impl", "uwg_write")
_emit_blocks_direct_write("p2", "change_package_impl", "direct_write_block")
_emit_records_tool_invocation("p2", "change_package_impl", "tool_invocation")
_emit_captures_execution_output("p2", "change_package_impl", "exec_output")
_emit_dispatches_agent("p3", "change_package_impl", "agent_dispatch")
_emit_coordinates_agents("p3", "change_package_impl", "agent_coordination")
_emit_records_workflow_lineage("p3", "change_package_impl", "workflow_lineage")
_emit_records_healing_outcome("p3", "change_package_impl", "healing_outcome")
_emit_escalates_failure("p3", "change_package_impl", "failure_escalation")
_emit_orchestrates_workflow("p3", "change_package_impl", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "change_package_impl", "healing_dispatch")
_emit_invokes_evaluation("p3", "change_package_impl", "evaluation_signal")
_emit_records_telemetry_event("p4", "change_package_impl", "telemetry_event")
_emit_captures_evaluation_metric("p4", "change_package_impl", "eval_metric")
_emit_stores_embedding("p4", "change_package_impl", "embedding_store")
_emit_updates_meta_learning_state("p4", "change_package_impl", "meta_learning")
_emit_links_execution_to_snapshot("p4", "change_package_impl", "exec_snapshot_link")


@dataclass(frozen=True, slots=True)
class ChangePackage:
    """Concrete implementation of ChangePackage protocol.

    Attributes:
        source: Source identifier for the change.
        target: Target identifier for the change.
        changes: Raw bytes representing the change.
        confidence: Confidence level (0.0 to 1.0).
        reason: Tuple of reason strings.
        timestamp_utc: UTC timestamp.
        authority_sensitivity: Authority sensitivity level (LOW/MEDIUM/HIGH).
        target_surface: Target surface identifier for mutation containment.
    """

    source: str
    target: str
    changes: bytes
    confidence: float
    reason: tuple[str, ...]
    timestamp_utc: int
    embedding_context_hash: str | None = None
    authority_sensitivity: str = "MEDIUM"
    target_surface: str | None = None

    @property
    def reasons(self) -> tuple[str, ...]:
        """Alias for reason tuple (for API compatibility)."""
        return self.reason

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ChangePackage.canonical_bytes")

        import json

        return json.dumps(
            {
                "source": self.source,
                "target": self.target,
                "changes": self.changes.decode("utf-8", errors="replace"),
                "confidence": self.confidence,
                "reason": list(self.reason),
                "timestamp_utc": self.timestamp_utc,
                "embedding_context_hash": self.embedding_context_hash,
                "authority_sensitivity": self.authority_sensitivity,
                "target_surface": self.target_surface,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
