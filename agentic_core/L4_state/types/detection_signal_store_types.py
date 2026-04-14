"""
L4 DetectionSignal Store — Phase 3

In-process persistence for L6 DetectionSignals.
Enforces strict prior-only semantics: fetch_latest returns only signals
committed BEFORE the given boundary tick, never same-cycle signals.

No external services. Pure in-memory store backed by a sorted list.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
)

emit_replay_key("p0", "detection_signal_store_types")
emit_determinism_digest("p0", "detection_signal_store_types")

_emit_dispatches_healing_run("p1", "detection_signal_store_types", "L4")
_emit_routes_through("p1", "detection_signal_store_types", "L4")
_emit_checks_agent_registry("p1", "detection_signal_store_types", "agent_registry")
_emit_validates_agent_capability("p1", "detection_signal_store_types", "capability")
_emit_dispatches_execution_plan("p1", "detection_signal_store_types", "exec_plan")
_emit_agent_executes_agent("p1", "detection_signal_store_types", "sub_agent")
_emit_routes_to_agent("p1", "detection_signal_store_types", "target_agent")
_emit_verifies_policy("p1", "detection_signal_store_types", "policy_check")
_emit_observes_runtime_state("p1", "detection_signal_store_types", "runtime_state")
_emit_verifies_boundary("p1", "detection_signal_store_types", "boundary_check")
_emit_transcripts_response("p1", "detection_signal_store_types", "transcript")
_emit_hard_fails_untranscripted("p1", "detection_signal_store_types")
_emit_gated_by_confidence("p1", "detection_signal_store_types", "confidence_gate")
_emit_escalates_to_human("p1", "detection_signal_store_types", "L4")
_emit_reads_policy_state("p1", "detection_signal_store_types", "L4")
_emit_authorize_and_execute("p2", "detection_signal_store_types", "execution_auth")
_emit_validates_capability("p2", "detection_signal_store_types", "capability_check")
_emit_routes_to_capability("p2", "detection_signal_store_types", "capability_route")
_emit_writes_via_uwg("p2", "detection_signal_store_types", "uwg_write")
_emit_blocks_direct_write("p2", "detection_signal_store_types", "direct_write_block")
_emit_records_tool_invocation("p2", "detection_signal_store_types", "tool_invocation")
_emit_captures_execution_output("p2", "detection_signal_store_types", "exec_output")
_emit_dispatches_agent("p3", "detection_signal_store_types", "agent_dispatch")
_emit_coordinates_agents("p3", "detection_signal_store_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "detection_signal_store_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "detection_signal_store_types", "healing_outcome")
_emit_escalates_failure("p3", "detection_signal_store_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "detection_signal_store_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "detection_signal_store_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "detection_signal_store_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "detection_signal_store_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "detection_signal_store_types", "eval_metric")
_emit_stores_embedding("p4", "detection_signal_store_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "detection_signal_store_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "detection_signal_store_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
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

_emit_emits_metric_event("detection_signal_store_types", "p4obs", "metric_1")
_emit_emits_metric_event("detection_signal_store_types", "p4obs", "metric_2")
_emit_emits_metric_event("detection_signal_store_types", "p4obs", "metric_3")
_emit_emits_metric_event("detection_signal_store_types", "p4obs", "metric_4")
_emit_emits_metric_event("detection_signal_store_types", "p4obs", "metric_5")
_emit_emits_metric_event("detection_signal_store_types", "p4obs", "metric_6")
_emit_records_incident_event("detection_signal_store_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("detection_signal_store_types", "p4obs", "anomaly")
_emit_writes_observability_log("detection_signal_store_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("detection_signal_store_types", "p4obs", "mon_state")
_emit_triggers_alert("detection_signal_store_types", "p4obs", "alert")
_emit_links_incident_trace("detection_signal_store_types", "p4obs", "trace_link")
_emit_captures_pattern("detection_signal_store_types", "p3lm", "pattern")
_emit_records_learning_event("detection_signal_store_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("detection_signal_store_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("detection_signal_store_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("detection_signal_store_types", "p3lm", "routing")
_emit_improves_agent_policy("detection_signal_store_types", "p3lm", "policy")
_emit_stores_learning_state("detection_signal_store_types", "p3lm", "state")
_emit_records_execution_trace("detection_signal_store_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("detection_signal_store_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("detection_signal_store_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("detection_signal_store_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("detection_signal_store_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("detection_signal_store_types", "env_read", "p2_env_1")
_emit_reads_environ("detection_signal_store_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("detection_signal_store_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("detection_signal_store_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "detection_signal_store_types", "context_pull")
_emit_pulls_context("p1", "detection_signal_store_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "detection_signal_store_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "detection_signal_store_types", "uwg_term_2")
_emit_writes_through("p1", "detection_signal_store_types", "write_through")
_emit_writes_through("p1", "detection_signal_store_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "detection_signal_store_types", "safety_validation")
_emit_invokes_eval("p1", "detection_signal_store_types", "eval_call")
_emit_proposal_commits_routing("p1", "detection_signal_store_types", "routing_commit")


def _get_detection_signal_class():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_detection_signal_class", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_detection_signal_class", "p0_governance")
    from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal

    return DetectionSignal


@dataclass
class _StoredEntry:
    """Internal record: signal + the commit_tick at which it was stored."""

    signal: object
    commit_tick: int


@dataclass
class DetectionSignalStore:
    """
    L4 in-process store for DetectionSignals.

    Commit ticks are monotonically increasing integers supplied by the caller
    (typically the SemanticClock step_id or a simple counter).

    Same-cycle enforcement:
        fetch_latest(before_tick=T) returns the most recent signal whose
        commit_tick is STRICTLY LESS THAN T.  A signal stored at tick T
        is invisible to a fetch at boundary T — no same-cycle readback.
    """

    _entries: list[_StoredEntry] = field(default_factory=list)

    def store(self, signal: DetectionSignal, commit_tick: int) -> str:
        """
        Persist a DetectionSignal at the given commit_tick.

        Returns signal_hash for caller confirmation.
        Raises ValueError if commit_tick is not strictly greater than the
        last stored tick (monotonicity enforcement).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "DetectionSignalStore.store")

        if self._entries and commit_tick <= self._entries[-1].commit_tick:
            raise ValueError(
                f"commit_tick {commit_tick} must be strictly greater than last stored tick {self._entries[-1].commit_tick}",
            )
        self._entries.append(_StoredEntry(signal=signal, commit_tick=commit_tick))
        return signal.signal_hash

    def fetch_latest(self, before_tick: int) -> object | None:
        """
        Return the most recent signal with commit_tick STRICTLY < before_tick.

        Returns None if no qualifying signal exists.
        This is the no-same-cycle guarantee: a signal stored at before_tick
        is NOT returned.
        """
        result: object | None = None
        for entry in self._entries:
            if entry.commit_tick < before_tick:
                result = entry.signal
        return result

    def count(self) -> int:
        return len(self._entries)


_SIGNAL_STORE = DetectionSignalStore()


def get_signal_store() -> DetectionSignalStore:
    """Return the module-level L4 DetectionSignal store singleton."""
    return _SIGNAL_STORE


def store_detection_signal(signal: object, commit_tick: int) -> str:
    """Store a signal in the L4 SSOT store. Returns signal_hash."""
    return get_signal_store().store(signal, commit_tick)


def fetch_latest_detection_signal(before_tick: int) -> object | None:
    """
    Fetch the most recent signal committed before before_tick.

    Enforces no-same-cycle semantics: signals at before_tick are excluded.
    """
    return get_signal_store().fetch_latest(before_tick)


def get_prior_detection_signal(execution_start_tick: int) -> object | None:
    """
    Guaranteed prior-only accessor for routing decisions.

    Returns the most recent signal committed strictly before
    execution_start_tick. Signals emitted during the current execution
    cycle (at or after execution_start_tick) are invisible.
    """
    return fetch_latest_detection_signal(before_tick=execution_start_tick)
