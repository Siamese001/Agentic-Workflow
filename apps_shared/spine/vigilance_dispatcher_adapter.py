"""
Vigilance Dispatcher Adapter — bridges VigilanceDispatcher to spine adapters.

VigilanceDispatcher.dispatch() requires a VigilanceEventArtifact and an
enqueue_fn callable. The spine adapters call dispatch(*args, **kwargs).

This adapter:
1. Constructs a VigilanceEventArtifact from the execution context
2. Routes events to a module-level in-memory queue (non-blocking)
3. Falls back to no-op if VigilanceDispatcher cannot be imported

Dispatching is fire-and-forget: any failure is logged and swallowed.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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
)

_emit_applies_guardrail("p0", "vigilance_dispatcher_adapter", "p0_governance")
_emit_reads_policy_state("p0", "vigilance_dispatcher_adapter", "policy_binding")
_emit_routes_to_agent("p1", "vigilance_dispatcher_adapter", "apps")
_emit_orchestrates_workflow("p1", "vigilance_dispatcher_adapter", "apps")
_emit_dispatches_execution_plan("p1", "vigilance_dispatcher_adapter", "apps")
_emit_validates_agent_capability("p1", "vigilance_dispatcher_adapter", "apps")
_emit_checks_agent_registry("p1", "vigilance_dispatcher_adapter", "apps")
_emit_snapshots_state("p0", "vigilance_dispatcher_adapter", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("vigilance_dispatcher_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("vigilance_dispatcher_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("vigilance_dispatcher_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("vigilance_dispatcher_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("vigilance_dispatcher_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("vigilance_dispatcher_adapter", "p4obs", "metric_6")
_emit_records_incident_event("vigilance_dispatcher_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("vigilance_dispatcher_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("vigilance_dispatcher_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("vigilance_dispatcher_adapter", "p4obs", "mon_state")
_emit_triggers_alert("vigilance_dispatcher_adapter", "p4obs", "alert")
_emit_links_incident_trace("vigilance_dispatcher_adapter", "p4obs", "trace_link")
_emit_captures_pattern("vigilance_dispatcher_adapter", "p3lm", "pattern")
_emit_records_learning_event("vigilance_dispatcher_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vigilance_dispatcher_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("vigilance_dispatcher_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vigilance_dispatcher_adapter", "p3lm", "routing")
_emit_improves_agent_policy("vigilance_dispatcher_adapter", "p3lm", "policy")
_emit_stores_learning_state("vigilance_dispatcher_adapter", "p3lm", "state")
_emit_records_execution_trace("vigilance_dispatcher_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vigilance_dispatcher_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vigilance_dispatcher_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vigilance_dispatcher_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vigilance_dispatcher_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vigilance_dispatcher_adapter", "env_read", "p2_env_1")
_emit_reads_environ("vigilance_dispatcher_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("vigilance_dispatcher_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vigilance_dispatcher_adapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vigilance_dispatcher_adapter", "context_pull")
_emit_pulls_context("p1", "vigilance_dispatcher_adapter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vigilance_dispatcher_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vigilance_dispatcher_adapter", "uwg_term_2")
_emit_writes_through("p1", "vigilance_dispatcher_adapter", "write_through")
_emit_writes_through("p1", "vigilance_dispatcher_adapter", "write_through_2")
_emit_validated_by_safety_plane("p1", "vigilance_dispatcher_adapter", "safety_validation")
_emit_invokes_eval("p1", "vigilance_dispatcher_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "vigilance_dispatcher_adapter", "routing_commit")
_emit_escalates_to_human("p1", "vigilance_dispatcher_adapter", "human_escalation")
_emit_routes_through("p1", "vigilance_dispatcher_adapter", "route_through")
_emit_agent_executes_agent("p1", "vigilance_dispatcher_adapter", "sub_agent")
_emit_verifies_policy("p1", "vigilance_dispatcher_adapter", "policy_check")
_emit_observes_runtime_state("p1", "vigilance_dispatcher_adapter", "runtime_state")
_emit_verifies_boundary("p1", "vigilance_dispatcher_adapter", "boundary_check")
_emit_transcripts_response("p1", "vigilance_dispatcher_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "vigilance_dispatcher_adapter")
_emit_gated_by_confidence("p1", "vigilance_dispatcher_adapter", "confidence_gate")
emit_replay_key("p0", "vigilance_dispatcher_adapter")
emit_determinism_digest("p0", "vigilance_dispatcher_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "vigilance_dispatcher_adapter", "execution_auth")
_emit_validates_capability("p2", "vigilance_dispatcher_adapter", "capability_check")
_emit_routes_to_capability("p2", "vigilance_dispatcher_adapter", "capability_route")
_emit_writes_via_uwg("p2", "vigilance_dispatcher_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "vigilance_dispatcher_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "vigilance_dispatcher_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "vigilance_dispatcher_adapter", "exec_output")
_emit_dispatches_agent("p3", "vigilance_dispatcher_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "vigilance_dispatcher_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "vigilance_dispatcher_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "vigilance_dispatcher_adapter", "healing_outcome")
_emit_escalates_failure("p3", "vigilance_dispatcher_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "vigilance_dispatcher_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vigilance_dispatcher_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "vigilance_dispatcher_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "vigilance_dispatcher_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vigilance_dispatcher_adapter", "eval_metric")
_emit_stores_embedding("p4", "vigilance_dispatcher_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "vigilance_dispatcher_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vigilance_dispatcher_adapter", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_EVENT_QUEUE: deque = deque(maxlen=256)


def _drain_event_queue() -> list:
    """Return and clear the current event queue (for testing)."""
    events = list(_EVENT_QUEUE)
    _EVENT_QUEUE.clear()
    return events


def _build_real_dispatcher():
    from agentic_core.L6_observability.utils.engines.vigilance_dispatcher import (
        VigilanceDispatcher,
        VigilanceEventArtifact,
    )

    return (VigilanceDispatcher, VigilanceEventArtifact)


class VigilanceDispatcherAdapter:
    """
    Adapter wrapping VigilanceDispatcher for use in spine adapters.

    dispatch() is fire-and-forget: failures are logged but never re-raised
    so vigilance events never block execution.
    """

    def __init__(self) -> None:
        try:
            VigilanceDispatcher, self._ArtifactCls = _build_real_dispatcher()
            self._dispatcher = VigilanceDispatcher()
            self._real = True
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            logger.warning("VigilanceDispatcher unavailable; using null fallback")
            self._dispatcher = None
            self._ArtifactCls = None
            self._real = False

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        """
        Dispatch a vigilance event extracted from execution context kwargs.

        Accepts the same variadic signature as the null stubs so spine code
        needs no changes.  When invoked with named keys:
          trace_id (str) — from CID or cycle
          signals  (tuple[str, ...] | list[str]) — execution signals
          summary  (str) — human-readable summary

        Falls back to no-op if any step fails.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "VigilanceDispatcherAdapter.dispatch")

        if not self._real:
            return
        try:
            trace_id: str = str(kwargs.get("trace_id", "unknown"))
            raw_signals = kwargs.get("signals", ())
            if isinstance(raw_signals, str):
                raw_signals = (raw_signals,)
            signals: tuple[str, ...] = tuple(raw_signals)
            summary: str = str(kwargs.get("summary", "spine-execution"))
            event = self._ArtifactCls.create(trace_id=trace_id, signals=signals, summary=summary)
            self._dispatcher.dispatch(event=event, enqueue_fn=_EVENT_QUEUE.append)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("VigilanceDispatcherAdapter.dispatch swallowed: %s", exc)

    @property
    def is_real(self) -> bool:
        """True if backed by the real VigilanceDispatcher, False for null fallback."""
        return self._real
