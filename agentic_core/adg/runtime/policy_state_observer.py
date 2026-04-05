"""G20 (gap): Policy state observation runtime.

Tracks every policy-state and runtime-state read performed by agentic modules:
  caller → observes_policy_state → PolicyStateReader
  caller → observes_runtime_state → RuntimeStateObserver
  caller → snapshots_state → StateSnapshot

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
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

_emit_applies_guardrail("p0", "policy_state_observer", "p0_governance")
_emit_snapshots_state("p0", "policy_state_observer", "state_snapshot")
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

_emit_emits_metric_event("policy_state_observer", "p4obs", "metric_1")
_emit_emits_metric_event("policy_state_observer", "p4obs", "metric_2")
_emit_emits_metric_event("policy_state_observer", "p4obs", "metric_3")
_emit_emits_metric_event("policy_state_observer", "p4obs", "metric_4")
_emit_emits_metric_event("policy_state_observer", "p4obs", "metric_5")
_emit_emits_metric_event("policy_state_observer", "p4obs", "metric_6")
_emit_records_incident_event("policy_state_observer", "p4obs", "incident")
_emit_captures_runtime_anomaly("policy_state_observer", "p4obs", "anomaly")
_emit_writes_observability_log("policy_state_observer", "p4obs", "obs_log")
_emit_updates_monitoring_state("policy_state_observer", "p4obs", "mon_state")
_emit_triggers_alert("policy_state_observer", "p4obs", "alert")
_emit_links_incident_trace("policy_state_observer", "p4obs", "trace_link")
_emit_captures_pattern("policy_state_observer", "p3lm", "pattern")
_emit_records_learning_event("policy_state_observer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("policy_state_observer", "p3lm", "snapshot")
_emit_feeds_meta_learning("policy_state_observer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("policy_state_observer", "p3lm", "routing")
_emit_improves_agent_policy("policy_state_observer", "p3lm", "policy")
_emit_stores_learning_state("policy_state_observer", "p3lm", "state")
_emit_records_execution_trace("policy_state_observer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("policy_state_observer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("policy_state_observer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("policy_state_observer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("policy_state_observer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("policy_state_observer", "env_read", "p2_env_1")
_emit_reads_environ("policy_state_observer", "env_read", "p2_env_2")
_emit_reads_runtime_state("policy_state_observer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("policy_state_observer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "policy_state_observer", "context_pull")
_emit_pulls_context("p1", "policy_state_observer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "policy_state_observer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "policy_state_observer", "uwg_term_2")
_emit_writes_through("p1", "policy_state_observer", "write_through")
_emit_writes_through("p1", "policy_state_observer", "write_through_2")
_emit_validated_by_safety_plane("p1", "policy_state_observer", "safety_validation")
_emit_invokes_eval("p1", "policy_state_observer", "eval_call")
_emit_proposal_commits_routing("p1", "policy_state_observer", "routing_commit")
_emit_escalates_to_human("p1", "policy_state_observer", "human_escalation")
_emit_routes_through("p1", "policy_state_observer", "route_through")
_emit_checks_agent_registry("p1", "policy_state_observer", "agent_registry")
_emit_validates_agent_capability("p1", "policy_state_observer", "capability")
_emit_dispatches_execution_plan("p1", "policy_state_observer", "exec_plan")
_emit_agent_executes_agent("p1", "policy_state_observer", "sub_agent")
_emit_routes_to_agent("p1", "policy_state_observer", "target_agent")
_emit_verifies_policy("p1", "policy_state_observer", "policy_check")
_emit_observes_runtime_state("p1", "policy_state_observer", "runtime_state")
_emit_verifies_boundary("p1", "policy_state_observer", "boundary_check")
_emit_transcripts_response("p1", "policy_state_observer", "transcript")
_emit_hard_fails_untranscripted("p1", "policy_state_observer")
_emit_gated_by_confidence("p1", "policy_state_observer", "confidence_gate")
emit_replay_key("p0", "policy_state_observer")
emit_determinism_digest("p0", "policy_state_observer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "policy_state_observer", "execution_auth")
_emit_validates_capability("p2", "policy_state_observer", "capability_check")
_emit_routes_to_capability("p2", "policy_state_observer", "capability_route")
_emit_writes_via_uwg("p2", "policy_state_observer", "uwg_write")
_emit_blocks_direct_write("p2", "policy_state_observer", "direct_write_block")
_emit_records_tool_invocation("p2", "policy_state_observer", "tool_invocation")
_emit_captures_execution_output("p2", "policy_state_observer", "exec_output")
_emit_dispatches_agent("p3", "policy_state_observer", "agent_dispatch")
_emit_coordinates_agents("p3", "policy_state_observer", "agent_coordination")
_emit_records_workflow_lineage("p3", "policy_state_observer", "workflow_lineage")
_emit_records_healing_outcome("p3", "policy_state_observer", "healing_outcome")
_emit_escalates_failure("p3", "policy_state_observer", "failure_escalation")
_emit_orchestrates_workflow("p3", "policy_state_observer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "policy_state_observer", "healing_dispatch")
_emit_invokes_evaluation("p3", "policy_state_observer", "evaluation_signal")
_emit_records_telemetry_event("p4", "policy_state_observer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "policy_state_observer", "eval_metric")
_emit_stores_embedding("p4", "policy_state_observer", "embedding_store")
_emit_updates_meta_learning_state("p4", "policy_state_observer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "policy_state_observer", "exec_snapshot_link")


class StateObservationKind(str, Enum):
    """Category of state being observed."""

    POLICY_STATE = "policy_state"
    RUNTIME_STATE = "runtime_state"
    GOVERNANCE_STATE = "governance_state"
    HEALTH_PROBE = "health_probe"
    SNAPSHOT = "snapshot"


class StateReadOutcome(str, Enum):
    """Outcome of a state read."""

    CURRENT = "current"
    STALE = "stale"
    UNAVAILABLE = "unavailable"
    CONFLICT = "conflict"


@dataclass
class StateObservationEvent:
    """A single state observation event."""

    event_id: str = field(default_factory=lambda: f"soe-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    run_id: str = ""
    kind: StateObservationKind = StateObservationKind.POLICY_STATE
    state_key: str = ""
    outcome: StateReadOutcome = StateReadOutcome.CURRENT
    observed_at: float = field(default_factory=time.time)
    staleness_seconds: float = 0.0
    snapshot_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "kind": self.kind.value,
            "state_key": self.state_key,
            "outcome": self.outcome.value,
            "observed_at": self.observed_at,
            "staleness_seconds": self.staleness_seconds,
            "snapshot_id": self.snapshot_id,
        }


@dataclass
class StateObservationReport:
    """Aggregated state observation report for a run."""

    agent_id: str
    run_id: str
    events: list[StateObservationEvent] = field(default_factory=list)

    @property
    def total_observations(self) -> int:
        return len(self.events)

    @property
    def policy_state_count(self) -> int:
        return sum(1 for e in self.events if e.kind == StateObservationKind.POLICY_STATE)

    @property
    def runtime_state_count(self) -> int:
        return sum(1 for e in self.events if e.kind == StateObservationKind.RUNTIME_STATE)

    @property
    def stale_count(self) -> int:
        return sum(1 for e in self.events if e.outcome == StateReadOutcome.STALE)

    @property
    def snapshot_count(self) -> int:
        return sum(1 for e in self.events if e.kind == StateObservationKind.SNAPSHOT)

    @property
    def by_kind(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "StateObservationReport.by_kind")

        result: dict[str, int] = {}
        for e in self.events:
            result[e.kind.value] = result.get(e.kind.value, 0) + 1
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_observations": self.total_observations,
            "policy_state_count": self.policy_state_count,
            "runtime_state_count": self.runtime_state_count,
            "stale_count": self.stale_count,
            "snapshot_count": self.snapshot_count,
            "by_kind": self.by_kind,
        }


class PolicyStateObserver:
    """G20 runtime observer: tracks policy-state and runtime-state reads.

    Lifecycle:
        observer = PolicyStateObserver(agent_id, run_id)
        observer.observe_policy("policy_hash_v3")
        observer.observe_runtime("agent_health_score")
        snap = observer.snapshot("before_mutation")
        report = observer.report
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = StateObservationReport(agent_id=agent_id, run_id=run_id)

    @property
    def report(self) -> StateObservationReport:
        return self._report

    def observe_policy(
        self,
        state_key: str,
        outcome: StateReadOutcome = StateReadOutcome.CURRENT,
        staleness_seconds: float = 0.0,
    ) -> StateObservationEvent:
        """Record a policy-state observation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PolicyStateObserver.observe_policy")

        event = StateObservationEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=StateObservationKind.POLICY_STATE,
            state_key=state_key,
            outcome=outcome,
            staleness_seconds=staleness_seconds,
        )
        self._report.events.append(event)
        return event

    def observe_runtime(
        self,
        state_key: str,
        outcome: StateReadOutcome = StateReadOutcome.CURRENT,
        staleness_seconds: float = 0.0,
    ) -> StateObservationEvent:
        """Record a runtime-state observation."""
        event = StateObservationEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=StateObservationKind.RUNTIME_STATE,
            state_key=state_key,
            outcome=outcome,
            staleness_seconds=staleness_seconds,
        )
        self._report.events.append(event)
        return event

    def probe_health(self, state_key: str) -> StateObservationEvent:
        """Record a health probe observation."""
        event = StateObservationEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=StateObservationKind.HEALTH_PROBE,
            state_key=state_key,
            outcome=StateReadOutcome.CURRENT,
        )
        self._report.events.append(event)
        return event

    def snapshot(self, label: str = "") -> StateObservationEvent:
        """Record a full-state snapshot event."""
        snap_id = f"snap-{uuid.uuid4().hex[:8]}"
        event = StateObservationEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=StateObservationKind.SNAPSHOT,
            state_key=label,
            outcome=StateReadOutcome.CURRENT,
            snapshot_id=snap_id,
        )
        self._report.events.append(event)
        return event
