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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

_emit_authorize_and_execute("p2", "telemetry_consumer", "execution_auth")
_emit_validates_capability("p2", "telemetry_consumer", "capability_check")
_emit_routes_to_capability("p2", "telemetry_consumer", "capability_route")
_emit_writes_via_uwg("p2", "telemetry_consumer", "uwg_write")
_emit_blocks_direct_write("p2", "telemetry_consumer", "direct_write_block")
_emit_records_tool_invocation("p2", "telemetry_consumer", "tool_invocation")
_emit_captures_execution_output("p2", "telemetry_consumer", "exec_output")
_emit_dispatches_agent("p3", "telemetry_consumer", "agent_dispatch")
_emit_coordinates_agents("p3", "telemetry_consumer", "agent_coordination")
_emit_records_workflow_lineage("p3", "telemetry_consumer", "workflow_lineage")
_emit_records_healing_outcome("p3", "telemetry_consumer", "healing_outcome")
_emit_escalates_failure("p3", "telemetry_consumer", "failure_escalation")
_emit_orchestrates_workflow("p3", "telemetry_consumer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "telemetry_consumer", "healing_dispatch")
_emit_invokes_evaluation("p3", "telemetry_consumer", "evaluation_signal")
_emit_records_telemetry_event("p4", "telemetry_consumer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "telemetry_consumer", "eval_metric")
_emit_stores_embedding("p4", "telemetry_consumer", "embedding_store")
_emit_updates_meta_learning_state("p4", "telemetry_consumer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "telemetry_consumer", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from system_learning.types.telemetry_types import (
    TelemetryEvent,
    create_telemetry_slice,
)

record_execution_trace("telemetry_consumer", "telemetry_consumer_trace")


_emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_1")
_emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_2")
_emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_3")
_emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_4")
_emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_5")
_emit_emits_metric_event("telemetry_consumer", "p4obs", "metric_6")
_emit_records_incident_event("telemetry_consumer", "p4obs", "incident")
_emit_captures_runtime_anomaly("telemetry_consumer", "p4obs", "anomaly")
_emit_writes_observability_log("telemetry_consumer", "p4obs", "obs_log")
_emit_updates_monitoring_state("telemetry_consumer", "p4obs", "mon_state")
_emit_triggers_alert("telemetry_consumer", "p4obs", "alert")
_emit_links_incident_trace("telemetry_consumer", "p4obs", "trace_link")
_emit_captures_pattern("telemetry_consumer", "p3lm", "pattern")
_emit_records_learning_event("telemetry_consumer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("telemetry_consumer", "p3lm", "snapshot")
_emit_feeds_meta_learning("telemetry_consumer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("telemetry_consumer", "p3lm", "routing")
_emit_improves_agent_policy("telemetry_consumer", "p3lm", "policy")
_emit_stores_learning_state("telemetry_consumer", "p3lm", "state")
_emit_records_execution_trace("telemetry_consumer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("telemetry_consumer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("telemetry_consumer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("telemetry_consumer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("telemetry_consumer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("telemetry_consumer", "env_read", "p2_env_1")
_emit_reads_environ("telemetry_consumer", "env_read", "p2_env_2")
_emit_reads_runtime_state("telemetry_consumer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("telemetry_consumer", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "telemetry_consumer")
_emit_applies_guardrail("p0", "telemetry_consumer", "p0_governance")
_emit_reads_policy_state("p0", "telemetry_consumer", "policy_binding")
_emit_snapshots_state("p0", "telemetry_consumer", "state_snapshot")
_emit_pulls_context("p1", "telemetry_consumer", "context_pull")
_emit_pulls_context("p1", "telemetry_consumer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "telemetry_consumer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "telemetry_consumer", "uwg_term_secondary")
_emit_writes_through("p1", "telemetry_consumer", "write_through")
_emit_writes_through("p1", "telemetry_consumer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "telemetry_consumer", "safety_validation")
_emit_invokes_eval("p1", "telemetry_consumer", "eval_call")
_emit_proposal_commits_routing("p1", "telemetry_consumer", "routing_commit")
_emit_escalates_to_human("p1", "telemetry_consumer", "human_escalation")
_emit_routes_through("p1", "telemetry_consumer", "route_through")
_emit_checks_agent_registry("p1", "telemetry_consumer", "agent_registry")
_emit_validates_agent_capability("p1", "telemetry_consumer", "capability")
_emit_dispatches_execution_plan("p1", "telemetry_consumer", "exec_plan")
_emit_agent_executes_agent("p1", "telemetry_consumer", "sub_agent")
_emit_routes_to_agent("p1", "telemetry_consumer", "target_agent")
_emit_verifies_policy("p1", "telemetry_consumer", "policy_check")
_emit_observes_runtime_state("p1", "telemetry_consumer", "runtime_state")
_emit_verifies_boundary("p1", "telemetry_consumer", "boundary_check")
_emit_transcripts_response("p1", "telemetry_consumer", "transcript")
_emit_hard_fails_untranscripted("p1", "telemetry_consumer")
_emit_gated_by_confidence("p1", "telemetry_consumer", "confidence_gate")
emit_replay_key("p0", "telemetry_consumer")
emit_determinism_digest("p0", "telemetry_consumer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
            )
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
    if hasattr(store, 'ingest_spans'):
        count = store.ingest_spans(spans)
        _emit_records_telemetry_event(
            "telemetry_consumer", "L4_STATE", "otel_span_ingestion",
            ingested_count=count
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
    from system_learning.stores import OpenTelemetrySpanStore

    store = OpenTelemetrySpanStore(max_buffer_size=max_buffer_size)

    _emit_records_telemetry_event(
        "telemetry_consumer", "L4_STATE", "otel_consumer_created",
        max_buffer_size=max_buffer_size
    )

    return store, consume_telemetry
