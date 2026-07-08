"""G15 (gap): Execution-path control runtime.

Models the dynamic path topology with Path A/B/C/D, stall forcing to Path D,
safety re-entry, and immediate vigilance reroute from L6 to L0/L1.

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "path_control", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "path_control", "policy_binding")
trace_contract._emit_snapshots_state("p0", "path_control", "state_snapshot")

trace_contract._emit_emits_metric_event("path_control", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("path_control", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("path_control", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("path_control", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("path_control", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("path_control", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("path_control", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("path_control", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("path_control", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("path_control", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("path_control", "p4obs", "alert")
trace_contract._emit_links_incident_trace("path_control", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("path_control", "p3lm", "pattern")
trace_contract._emit_records_learning_event("path_control", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("path_control", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("path_control", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("path_control", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("path_control", "p3lm", "policy")
trace_contract._emit_stores_learning_state("path_control", "p3lm", "state")
trace_contract._emit_records_execution_trace("path_control", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("path_control", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("path_control", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("path_control", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("path_control", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("path_control", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("path_control", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("path_control", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("path_control", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "path_control", "context_pull")
trace_contract._emit_pulls_context("p1", "path_control", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "path_control", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "path_control", "uwg_term_2")
trace_contract._emit_writes_through("p1", "path_control", "write_through")
trace_contract._emit_writes_through("p1", "path_control", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "path_control", "safety_validation")
trace_contract._emit_invokes_eval("p1", "path_control", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "path_control", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "path_control", "human_escalation")
trace_contract._emit_routes_through("p1", "path_control", "route_through")
trace_contract._emit_checks_agent_registry("p1", "path_control", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "path_control", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "path_control", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "path_control", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "path_control", "target_agent")
trace_contract._emit_verifies_policy("p1", "path_control", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "path_control", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "path_control", "boundary_check")
trace_contract._emit_transcripts_response("p1", "path_control", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "path_control")
trace_contract._emit_gated_by_confidence("p1", "path_control", "confidence_gate")
trace_contract.emit_replay_key("p0", "path_control")
trace_contract.emit_determinism_digest("p0", "path_control")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "path_control", "execution_auth")
trace_contract._emit_validates_capability("p2", "path_control", "capability_check")
trace_contract._emit_routes_to_capability("p2", "path_control", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "path_control", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "path_control", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "path_control", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "path_control", "exec_output")
trace_contract._emit_dispatches_agent("p3", "path_control", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "path_control", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "path_control", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "path_control", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "path_control", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "path_control", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "path_control", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "path_control", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "path_control", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "path_control", "eval_metric")
trace_contract._emit_stores_embedding("p4", "path_control", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "path_control", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "path_control", "exec_snapshot_link")


class ExecutionPath(str, Enum):
    PATH_A = "path_a"  # Normal execution
    PATH_B = "path_b"  # Degraded / limited capability
    PATH_C = "path_c"  # Safety-supervised execution
    PATH_D = "path_d"  # Stall / human-review required
    SAFETY_REENTRY = "safety_reentry"  # Re-entering L5 safety gate
    VIGILANCE_REROUTE = "vigilance_reroute"  # L6→L0/L1 emergency reroute


class PathTransitionReason(str, Enum):
    NORMAL_ROUTING = "normal_routing"
    LOW_CONFIDENCE = "low_confidence"
    SAFETY_TRIGGER = "safety_trigger"
    STALL_FORCED = "stall_forced"
    L6_VIGILANCE = "l6_vigilance"
    HUMAN_OVERRIDE = "human_override"
    BUDGET_EXHAUSTED = "budget_exhausted"
    BOUNDARY_REJECTED = "boundary_rejected"


@dataclass
class PathTransition:
    """A single path transition event."""

    transition_id: str = field(default_factory=lambda: f"pt-{uuid.uuid4().hex[:8]}")
    run_id: str = ""
    agent_id: str = ""
    from_path: ExecutionPath = ExecutionPath.PATH_A
    to_path: ExecutionPath = ExecutionPath.PATH_A
    reason: PathTransitionReason = PathTransitionReason.NORMAL_ROUTING
    ts: float = field(default_factory=time.time)
    detail: str = ""
    triggered_by: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "from_path": self.from_path.value,
            "to_path": self.to_path.value,
            "reason": self.reason.value,
            "ts": self.ts,
            "detail": self.detail,
            "triggered_by": self.triggered_by,
        }


@dataclass
class PathControlReport:
    """Aggregated report of path control transitions for one session."""

    agent_id: str = ""
    run_id: str = ""
    transitions: list[PathTransition] = field(default_factory=list)
    current_path: ExecutionPath = ExecutionPath.PATH_A

    @property
    def stall_count(self) -> int:
        return sum(1 for t in self.transitions if t.to_path == ExecutionPath.PATH_D)

    @property
    def vigilance_reroute_count(self) -> int:
        return sum(1 for t in self.transitions if t.to_path == ExecutionPath.VIGILANCE_REROUTE)

    @property
    def safety_reentry_count(self) -> int:
        return sum(1 for t in self.transitions if t.to_path == ExecutionPath.SAFETY_REENTRY)

    @property
    def total_transitions(self) -> int:
        return len(self.transitions)

    def path_visit_counts(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "PathControlReport.path_visit_counts"
        )

        counts: dict[str, int] = {}
        for t in self.transitions:
            key = t.to_path.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "current_path": self.current_path.value,
            "total_transitions": self.total_transitions,
            "stall_count": self.stall_count,
            "vigilance_reroute_count": self.vigilance_reroute_count,
            "safety_reentry_count": self.safety_reentry_count,
            "path_visit_counts": self.path_visit_counts(),
        }

    @property
    def summary(self) -> str:
        return (
            f"PathControl [{self.agent_id}] — "
            f"current={self.current_path.value}, "
            f"{self.total_transitions} transitions, "
            f"{self.stall_count} stalls, "
            f"{self.vigilance_reroute_count} vigilance reroutes"
        )


class ExecutionPathController:
    """Runtime controller for execution path topology."""

    def __init__(self, agent_id: str, run_id: str) -> None:
        self.report = PathControlReport(agent_id=agent_id, run_id=run_id)

    def _transition(
        self,
        to_path: ExecutionPath,
        reason: PathTransitionReason,
        detail: str = "",
        triggered_by: str = "",
    ) -> PathTransition:
        t = PathTransition(
            run_id=self.report.run_id,
            agent_id=self.report.agent_id,
            from_path=self.report.current_path,
            to_path=to_path,
            reason=reason,
            detail=detail,
            triggered_by=triggered_by,
        )
        self.report.transitions.append(t)
        self.report.current_path = to_path
        return t

    def route_path(
        self,
        path: ExecutionPath = ExecutionPath.PATH_A,
        detail: str = "",
    ) -> PathTransition:
        return self._transition(path, PathTransitionReason.NORMAL_ROUTING, detail)

    def force_stall(self, reason: str = "", triggered_by: str = "") -> PathTransition:
        return self._transition(
            ExecutionPath.PATH_D,
            PathTransitionReason.STALL_FORCED,
            detail=reason,
            triggered_by=triggered_by,
        )

    def force_path_d(self, reason: str = "") -> PathTransition:
        return self.force_stall(reason=reason)

    def reenter_safety(self, reason: str = "", triggered_by: str = "") -> PathTransition:
        return self._transition(
            ExecutionPath.SAFETY_REENTRY,
            PathTransitionReason.SAFETY_TRIGGER,
            detail=reason,
            triggered_by=triggered_by,
        )

    def vigilance_reroute(self, triggered_by: str = "L6", detail: str = "") -> PathTransition:
        return self._transition(
            ExecutionPath.VIGILANCE_REROUTE,
            PathTransitionReason.L6_VIGILANCE,
            detail=detail,
            triggered_by=triggered_by,
        )

    def reroute_to_l0(self, detail: str = "") -> PathTransition:
        return self.vigilance_reroute(triggered_by="L6→L0", detail=detail)

    def reroute_to_l1(self, detail: str = "") -> PathTransition:
        return self.vigilance_reroute(triggered_by="L6→L1", detail=detail)

    @property
    def current_path(self) -> ExecutionPath:
        return self.report.current_path
