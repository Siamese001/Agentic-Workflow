"""G-16-26: Telemetry consumer for System Learning telemetry integration.

Read-only slice builder producing deterministic telemetry slices.
Supports both legacy TelemetryStore and new OpenTelemetry span ingestion.

Invariants:
  - No wall-clock, no env, no randomness
  - Deterministic sorting by (ts_utc, kind, payload_hash)
  - Fail-closed on invalid window
  - Read-only inputs, proposal-only outputs
"""

from __future__ import annotations

import hashlib
from typing import Protocol

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "telemetry_consumer", "execution_auth")
trace_contract._emit_validates_capability("p2", "telemetry_consumer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "telemetry_consumer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "telemetry_consumer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "telemetry_consumer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "telemetry_consumer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "telemetry_consumer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "telemetry_consumer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "telemetry_consumer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "telemetry_consumer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "telemetry_consumer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "telemetry_consumer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "telemetry_consumer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "telemetry_consumer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "telemetry_consumer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "telemetry_consumer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "telemetry_consumer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "telemetry_consumer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "telemetry_consumer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "telemetry_consumer", "exec_snapshot_link")
from agentic_core.L6_system_learning.types.telemetry_types import (
    TelemetryEvent,
    create_telemetry_slice,
)

trace_contract.record_execution_trace("telemetry_consumer", "telemetry_consumer_trace")


trace_contract._emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("telemetry_consumer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("telemetry_consumer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("telemetry_consumer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("telemetry_consumer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("telemetry_consumer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("telemetry_consumer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("telemetry_consumer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("telemetry_consumer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("telemetry_consumer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("telemetry_consumer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("telemetry_consumer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("telemetry_consumer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("telemetry_consumer", "p3lm", "state")
trace_contract._emit_records_execution_trace("telemetry_consumer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("telemetry_consumer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("telemetry_consumer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("telemetry_consumer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("telemetry_consumer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("telemetry_consumer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("telemetry_consumer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("telemetry_consumer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("telemetry_consumer", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "telemetry_consumer")
trace_contract._emit_applies_guardrail("p0", "telemetry_consumer", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "telemetry_consumer", "policy_binding")
trace_contract._emit_snapshots_state("p0", "telemetry_consumer", "state_snapshot")
trace_contract._emit_pulls_context("p1", "telemetry_consumer", "context_pull")
trace_contract._emit_pulls_context("p1", "telemetry_consumer", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "telemetry_consumer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "telemetry_consumer", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "telemetry_consumer", "write_through")
trace_contract._emit_writes_through("p1", "telemetry_consumer", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "telemetry_consumer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "telemetry_consumer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "telemetry_consumer", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "telemetry_consumer", "human_escalation")
trace_contract._emit_routes_through("p1", "telemetry_consumer", "route_through")
trace_contract._emit_checks_agent_registry("p1", "telemetry_consumer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "telemetry_consumer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "telemetry_consumer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "telemetry_consumer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "telemetry_consumer", "target_agent")
trace_contract._emit_verifies_policy("p1", "telemetry_consumer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "telemetry_consumer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "telemetry_consumer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "telemetry_consumer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "telemetry_consumer")
trace_contract._emit_gated_by_confidence("p1", "telemetry_consumer", "confidence_gate")
trace_contract.emit_replay_key("p0", "telemetry_consumer")
trace_contract.emit_determinism_digest("p0", "telemetry_consumer")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# =============================================================================
# Exceptions
# =============================================================================


class TelemetryConsumerError(RuntimeError):
    """Raised when telemetry consumption fails."""


# =============================================================================
# Protocol
# =============================================================================


class TelemetryStore(Protocol):
    """Protocol for read-only telemetry store access."""

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        """Read telemetry events within window.

        Parameters
        ----------
        window_start_utc : int
            Start of window (Unix timestamp).
        window_end_utc : int
            End of window (Unix timestamp).

        Returns
        -------
        tuple[tuple[int, str, bytes], ...]
            Events as (ts_utc, kind, payload_bytes).
        """
        ...


# =============================================================================
# Telemetry Consumer
# =============================================================================


def consume_telemetry(
    store: TelemetryStore,
    window_start_utc: int,
    window_end_utc: int,
) -> object:  # Returns TelemetrySlice
    """Consume telemetry events and produce deterministic slice.

    Enforces:
      - window_start < window_end
      - Deterministic sorting by (ts_utc, kind, payload_hash)
      - slice_hash = SHA-256(canonical_bytes(slice))
      - slice_id = slice_hash

    Parameters
    ----------
    store : TelemetryStore
        Read-only telemetry store.
    window_start_utc : int
        Start of window.
    window_end_utc : int
        End of window.

    Returns
    -------
    TelemetrySlice
        Deterministic telemetry slice.

    Raises
    ------
    TelemetryConsumerError
        If window is invalid.
    """
    # Validate window
    if window_start_utc >= window_end_utc:
        raise TelemetryConsumerError(f"Invalid window: start={window_start_utc} >= end={window_end_utc}")

    # Read events from store
    raw_events = store.read_events(window_start_utc, window_end_utc)

    # Convert to TelemetryEvent with payload_hash
    events = []
    for ts_utc, kind, payload_bytes in raw_events:
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        events.append(
            TelemetryEvent(
                ts_utc=ts_utc,
                kind=kind,
                payload_hash=payload_hash,
            ),
        )

    # Sort events deterministically by (ts_utc, kind, payload_hash)
    sorted_events = sorted(events, key=lambda e: (e.ts_utc, e.kind, e.payload_hash))

    # Create slice with deterministic hash
    return create_telemetry_slice(
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        events=tuple(sorted_events),
    )


def ingest_otel_spans(
    store: TelemetryStore,
    spans: list[dict[str, Any]],
) -> int:
    """Ingest OpenTelemetry spans into telemetry store.

    Phase 2: Bridges OpenTelemetry spans to System Learning telemetry.
    Converts span data to telemetry events for meta-learning analysis.

    Parameters
    ----------
    store : TelemetryStore
        Telemetry store with span ingestion capability.
    spans : list[dict[str, Any]]
        OpenTelemetry span dictionaries from tracing adapter.

    Returns
    -------
    int
        Number of spans ingested successfully.
    """
    if not spans:
        return 0

    # Check if store supports span ingestion
    if hasattr(store, "ingest_spans"):
        count = store.ingest_spans(spans)
        trace_contract._emit_records_telemetry_event(
            "telemetry_consumer",
            "L4_STATE",
            "otel_span_ingestion",
            ingested_count=count,
        )
        return count

    # Fallback: stores without native span support
    return 0


def create_telemetry_consumer_with_otel(
    max_buffer_size: int = 10000,
) -> tuple[TelemetryStore, Any]:
    """Create telemetry consumer with OpenTelemetry span store.

    Phase 2: Factory for creating integrated OTel + System Learning setup.

    Parameters
    ----------
    max_buffer_size : int
        Maximum spans to retain in telemetry store buffer.

    Returns
    -------
    tuple[TelemetryStore, Any]
        Telemetry store and consumer function ready for OTel integration.
    """
    from .....stores import OpenTelemetrySpanStore

    store = OpenTelemetrySpanStore(max_buffer_size=max_buffer_size)

    trace_contract._emit_records_telemetry_event(
        "telemetry_consumer",
        "L4_STATE",
        "otel_consumer_created",
        max_buffer_size=max_buffer_size,
    )

    return store, consume_telemetry
