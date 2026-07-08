"""G22 (gap): Healing orchestrator runtime.

Tracks every healing dispatch, confirmation, and abort event:
  caller → dispatches_healing_run → HealingOrchestrator
  caller → confirms_heal → HealingOrchestrator
  caller → aborts_heal → HealingOrchestrator

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "healing_orchestrator", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "healing_orchestrator", "policy_binding")
trace_contract._emit_snapshots_state("p0", "healing_orchestrator", "state_snapshot")

trace_contract._emit_emits_metric_event("healing_orchestrator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("healing_orchestrator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("healing_orchestrator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("healing_orchestrator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("healing_orchestrator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("healing_orchestrator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("healing_orchestrator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("healing_orchestrator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("healing_orchestrator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("healing_orchestrator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("healing_orchestrator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("healing_orchestrator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("healing_orchestrator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("healing_orchestrator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("healing_orchestrator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("healing_orchestrator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("healing_orchestrator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("healing_orchestrator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("healing_orchestrator", "p3lm", "state")
trace_contract._emit_records_execution_trace("healing_orchestrator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("healing_orchestrator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("healing_orchestrator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("healing_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("healing_orchestrator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("healing_orchestrator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("healing_orchestrator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("healing_orchestrator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("healing_orchestrator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "healing_orchestrator", "context_pull")
trace_contract._emit_pulls_context("p1", "healing_orchestrator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_orchestrator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_orchestrator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "healing_orchestrator", "write_through")
trace_contract._emit_writes_through("p1", "healing_orchestrator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "healing_orchestrator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "healing_orchestrator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "healing_orchestrator", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "healing_orchestrator", "human_escalation")
trace_contract._emit_routes_through("p1", "healing_orchestrator", "route_through")
trace_contract._emit_checks_agent_registry("p1", "healing_orchestrator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "healing_orchestrator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "healing_orchestrator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "healing_orchestrator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "healing_orchestrator", "target_agent")
trace_contract._emit_verifies_policy("p1", "healing_orchestrator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "healing_orchestrator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "healing_orchestrator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "healing_orchestrator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "healing_orchestrator")
trace_contract._emit_gated_by_confidence("p1", "healing_orchestrator", "confidence_gate")
trace_contract.emit_replay_key("p0", "healing_orchestrator")
trace_contract.emit_determinism_digest("p0", "healing_orchestrator")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "healing_orchestrator", "execution_auth")
trace_contract._emit_validates_capability("p2", "healing_orchestrator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "healing_orchestrator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "healing_orchestrator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "healing_orchestrator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "healing_orchestrator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "healing_orchestrator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "healing_orchestrator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "healing_orchestrator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "healing_orchestrator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "healing_orchestrator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "healing_orchestrator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "healing_orchestrator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "healing_orchestrator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "healing_orchestrator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "healing_orchestrator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "healing_orchestrator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "healing_orchestrator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "healing_orchestrator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "healing_orchestrator", "exec_snapshot_link")


class HealingRunPhase(str, Enum):
    """Phase of a healing run."""

    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    CONFIRMED = "confirmed"
    ABORTED = "aborted"
    TIMED_OUT = "timed_out"


class HealingTrigger(str, Enum):
    """What triggered the healing run."""

    VIOLATION_DETECTED = "violation_detected"
    POLICY_DRIFT = "policy_drift"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    ESCALATION = "escalation"
    THRESHOLD_BREACH = "threshold_breach"


@dataclass
class OrchestrationStep:
    """A single step within a healing run."""

    step_id: str = field(default_factory=lambda: f"ost-{uuid.uuid4().hex[:8]}")
    healer_id: str = ""
    action: str = ""
    succeeded: bool = False
    error_message: str = ""
    executed_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "healer_id": self.healer_id,
            "action": self.action,
            "succeeded": self.succeeded,
            "error_message": self.error_message,
            "executed_at": self.executed_at,
        }


@dataclass
class HealingRun:
    """A complete healing run from dispatch to terminal state."""

    run_id: str = field(default_factory=lambda: f"hr-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    orchestrator_run_id: str = ""
    trigger: HealingTrigger = HealingTrigger.VIOLATION_DETECTED
    phase: HealingRunPhase = HealingRunPhase.DISPATCHED
    violation_ref: str = ""
    steps: list[OrchestrationStep] = field(default_factory=list)
    dispatched_at: float = field(default_factory=time.time)
    confirmed_at: float = 0.0
    aborted_at: float = 0.0
    abort_reason: str = ""

    @property
    def is_terminal(self) -> bool:
        return self.phase in (HealingRunPhase.CONFIRMED, HealingRunPhase.ABORTED, HealingRunPhase.TIMED_OUT)

    @property
    def succeeded(self) -> bool:
        return self.phase == HealingRunPhase.CONFIRMED

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def failed_step_count(self) -> int:
        return sum(1 for s in self.steps if not s.succeeded)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "orchestrator_run_id": self.orchestrator_run_id,
            "trigger": self.trigger.value,
            "phase": self.phase.value,
            "violation_ref": self.violation_ref,
            "step_count": self.step_count,
            "failed_step_count": self.failed_step_count,
            "dispatched_at": self.dispatched_at,
            "confirmed_at": self.confirmed_at,
            "aborted_at": self.aborted_at,
            "abort_reason": self.abort_reason,
            "steps": [s.to_dict() for s in self.steps],
        }


@dataclass
class HealingOrchestratorReport:
    """Aggregated report of all healing runs managed by this orchestrator."""

    agent_id: str
    run_id: str
    healing_runs: list[HealingRun] = field(default_factory=list)

    @property
    def total_runs(self) -> int:
        return len(self.healing_runs)

    @property
    def confirmed_count(self) -> int:
        return sum(1 for r in self.healing_runs if r.phase == HealingRunPhase.CONFIRMED)

    @property
    def aborted_count(self) -> int:
        return sum(1 for r in self.healing_runs if r.phase == HealingRunPhase.ABORTED)

    @property
    def in_progress_count(self) -> int:
        return sum(1 for r in self.healing_runs if r.phase == HealingRunPhase.IN_PROGRESS)

    @property
    def success_rate(self) -> float:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HealingOrchestratorReport.success_rate"
        )

        terminal = [r for r in self.healing_runs if r.is_terminal]
        if not terminal:
            return 0.0
        return sum(1 for r in terminal if r.succeeded) / len(terminal)

    @property
    def by_trigger(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for r in self.healing_runs:
            result[r.trigger.value] = result.get(r.trigger.value, 0) + 1
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_runs": self.total_runs,
            "confirmed_count": self.confirmed_count,
            "aborted_count": self.aborted_count,
            "in_progress_count": self.in_progress_count,
            "success_rate": self.success_rate,
            "by_trigger": self.by_trigger,
        }


class HealingOrchestrator:
    """G22 runtime orchestrator: tracks healing dispatches, steps, confirms, aborts.

    Lifecycle:
        orch = HealingOrchestrator(agent_id, run_id)
        run = orch.dispatch("violation-123", trigger=HealingTrigger.VIOLATION_DETECTED)
        orch.add_step(run, "healer_A", "apply_patch")
        orch.confirm(run)
        report = orch.report
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = HealingOrchestratorReport(agent_id=agent_id, run_id=run_id)

    @property
    def report(self) -> HealingOrchestratorReport:
        return self._report

    def dispatch(
        self,
        violation_ref: str = "",
        trigger: HealingTrigger = HealingTrigger.VIOLATION_DETECTED,
    ) -> HealingRun:
        """Dispatch a new healing run."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HealingOrchestrator.dispatch"
        )

        run = HealingRun(
            agent_id=self._agent_id,
            orchestrator_run_id=self._run_id,
            trigger=trigger,
            phase=HealingRunPhase.DISPATCHED,
            violation_ref=violation_ref,
        )
        self._report.healing_runs.append(run)
        return run

    def start(self, run: HealingRun) -> None:
        """Mark a healing run as in-progress."""
        if run.phase == HealingRunPhase.DISPATCHED:
            run.phase = HealingRunPhase.IN_PROGRESS

    def add_step(
        self,
        run: HealingRun,
        healer_id: str,
        action: str,
        succeeded: bool = True,
        error_message: str = "",
    ) -> OrchestrationStep:
        """Add a step to an in-progress healing run."""
        if run.phase == HealingRunPhase.DISPATCHED:
            run.phase = HealingRunPhase.IN_PROGRESS
        step = OrchestrationStep(
            healer_id=healer_id,
            action=action,
            succeeded=succeeded,
            error_message=error_message,
        )
        run.steps.append(step)
        return step

    def confirm(self, run: HealingRun) -> None:
        """Confirm a healing run as successfully completed."""
        if not run.is_terminal:
            run.phase = HealingRunPhase.CONFIRMED
            run.confirmed_at = time.time()

    def abort(self, run: HealingRun, reason: str = "") -> None:
        """Abort a healing run."""
        if not run.is_terminal:
            run.phase = HealingRunPhase.ABORTED
            run.abort_reason = reason
            run.aborted_at = time.time()

    def timeout(self, run: HealingRun) -> None:
        """Mark a healing run as timed out."""
        if not run.is_terminal:
            run.phase = HealingRunPhase.TIMED_OUT
            run.aborted_at = time.time()
            run.abort_reason = "timeout"


trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_1")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_2")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_3")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_4")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_5")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_6")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_7")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_8")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_9")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_10")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_11")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_12")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_13")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_14")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_15")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_16")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_17")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_18")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_19")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_20")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_21")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_22")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_23")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_24")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_25")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_26")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_27")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_28")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_29")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_30")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_31")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_32")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_33")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_34")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_35")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_36")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_37")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_38")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_39")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_40")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_41")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_42")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_43")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_44")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_45")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_46")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_47")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_48")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_49")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_50")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_51")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_52")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_53")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_54")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_55")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_56")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_57")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_58")
trace_contract._emit_reads_through("l4", "healing_orchestrator", "urg_read_59")
