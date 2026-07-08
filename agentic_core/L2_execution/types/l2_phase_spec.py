"""
Data-only module. No business logic, no healing, no orchestration. SSOT ordering.
Pins the canonical phase ordering extracted from ``execute_ssot._legacy_main``
to prevent accidental monolith reconstitution and to anchor future healer
Phase ordering (legacy mirror):
    1. pre_audit
    2. discovery
    3. reconciliation
    4. alignment
    5. arch_validation
    6. healing
    7. certification
"""

from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("l2_phase_spec", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("l2_phase_spec", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("l2_phase_spec", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("l2_phase_spec", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("l2_phase_spec", "p4obs", "alert")
trace_contract._emit_links_incident_trace("l2_phase_spec", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("l2_phase_spec", "p3lm", "pattern")
trace_contract._emit_records_learning_event("l2_phase_spec", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("l2_phase_spec", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("l2_phase_spec", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("l2_phase_spec", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("l2_phase_spec", "p3lm", "policy")
trace_contract._emit_stores_learning_state("l2_phase_spec", "p3lm", "state")
trace_contract._emit_records_execution_trace("l2_phase_spec", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("l2_phase_spec", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("l2_phase_spec", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("l2_phase_spec", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("l2_phase_spec", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("l2_phase_spec", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("l2_phase_spec", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("l2_phase_spec", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("l2_phase_spec", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "l2_phase_spec")
trace_contract.emit_determinism_digest("p0", "l2_phase_spec")

trace_contract._emit_dispatches_healing_run("p1", "l2_phase_spec", "L2")
trace_contract._emit_routes_through("p1", "l2_phase_spec", "L2")
trace_contract._emit_checks_agent_registry("p1", "l2_phase_spec", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "l2_phase_spec", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "l2_phase_spec", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "l2_phase_spec", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "l2_phase_spec", "target_agent")
trace_contract._emit_verifies_policy("p1", "l2_phase_spec", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "l2_phase_spec", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "l2_phase_spec", "boundary_check")
trace_contract._emit_transcripts_response("p1", "l2_phase_spec", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "l2_phase_spec")
trace_contract._emit_gated_by_confidence("p1", "l2_phase_spec", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "l2_phase_spec", "L2")
trace_contract._emit_reads_policy_state("p1", "l2_phase_spec", "L2")
trace_contract._emit_pulls_context("p1", "l2_phase_spec", "context_pull")
trace_contract._emit_pulls_context("p1", "l2_phase_spec", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "l2_phase_spec", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "l2_phase_spec", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "l2_phase_spec", "write_through")
trace_contract._emit_writes_through("p1", "l2_phase_spec", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "l2_phase_spec", "safety_validation")
trace_contract._emit_invokes_eval("p1", "l2_phase_spec", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "l2_phase_spec", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "l2_phase_spec")
trace_contract._emit_applies_guardrail("p0", "l2_phase_spec", "p0_governance")
trace_contract._emit_snapshots_state("p0", "l2_phase_spec", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "l2_phase_spec", "execution_auth")
trace_contract._emit_validates_capability("p2", "l2_phase_spec", "capability_check")
trace_contract._emit_routes_to_capability("p2", "l2_phase_spec", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "l2_phase_spec", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "l2_phase_spec", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "l2_phase_spec", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "l2_phase_spec", "exec_output")
trace_contract._emit_dispatches_agent("p3", "l2_phase_spec", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "l2_phase_spec", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "l2_phase_spec", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "l2_phase_spec", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "l2_phase_spec", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "l2_phase_spec", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "l2_phase_spec", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "l2_phase_spec", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "l2_phase_spec", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "l2_phase_spec", "eval_metric")
trace_contract._emit_stores_embedding("p4", "l2_phase_spec", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "l2_phase_spec", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "l2_phase_spec", "exec_snapshot_link")


@dataclass(frozen=True, slots=True)
class PhaseSpec:
    """Immutable specification for a single execution phase.

    Attributes:
        name: Canonical phase name (unique within a plan).
        guardian_ids: Guardian IDs to run before this phase (empty for now).
        healer_ids: Healer IDs to invoke during this phase (empty for now).
        rerun_guardians: Guardian IDs to re-run after healing (empty for now).
        approval_required: Whether human approval is needed (False for now).
        inputs_from_prior: Phase names whose outputs feed this phase (empty for now).
    """

    name: str
    guardian_ids: tuple[str, ...] = ()
    healer_ids: tuple[str, ...] = ()
    rerun_guardians: tuple[str, ...] = ()
    approval_required: bool = False
    inputs_from_prior: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class L2ExecutionPlan:
    """Immutable, ordered sequence of PhaseSpecs defining an execution plan."""

    phases: tuple[PhaseSpec, ...]


LEGACY_MIRROR_PLAN: L2ExecutionPlan = L2ExecutionPlan(
    phases=(
        PhaseSpec(name="pre_audit"),
        PhaseSpec(name="discovery"),
        PhaseSpec(name="reconciliation"),
        PhaseSpec(name="alignment"),
        PhaseSpec(name="arch_validation"),
        PhaseSpec(name="healing"),
        PhaseSpec(name="certification"),
    ),
)
__all__ = ["L2ExecutionPlan", "LEGACY_MIRROR_PLAN", "PhaseSpec"]
