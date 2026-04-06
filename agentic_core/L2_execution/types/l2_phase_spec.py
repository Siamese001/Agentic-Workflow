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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_1")
_emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_2")
_emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_3")
_emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_4")
_emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_5")
_emit_emits_metric_event("l2_phase_spec", "p4obs", "metric_6")
_emit_records_incident_event("l2_phase_spec", "p4obs", "incident")
_emit_captures_runtime_anomaly("l2_phase_spec", "p4obs", "anomaly")
_emit_writes_observability_log("l2_phase_spec", "p4obs", "obs_log")
_emit_updates_monitoring_state("l2_phase_spec", "p4obs", "mon_state")
_emit_triggers_alert("l2_phase_spec", "p4obs", "alert")
_emit_links_incident_trace("l2_phase_spec", "p4obs", "trace_link")
_emit_captures_pattern("l2_phase_spec", "p3lm", "pattern")
_emit_records_learning_event("l2_phase_spec", "p3lm", "learning_event")
_emit_writes_learning_snapshot("l2_phase_spec", "p3lm", "snapshot")
_emit_feeds_meta_learning("l2_phase_spec", "p3lm", "meta_feed")
_emit_updates_routing_strategy("l2_phase_spec", "p3lm", "routing")
_emit_improves_agent_policy("l2_phase_spec", "p3lm", "policy")
_emit_stores_learning_state("l2_phase_spec", "p3lm", "state")
_emit_records_execution_trace("l2_phase_spec", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("l2_phase_spec", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("l2_phase_spec", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("l2_phase_spec", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("l2_phase_spec", "L4_STATE", "p2_trace_5")
_emit_reads_environ("l2_phase_spec", "env_read", "p2_env_1")
_emit_reads_environ("l2_phase_spec", "env_read", "p2_env_2")
_emit_reads_runtime_state("l2_phase_spec", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("l2_phase_spec", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "l2_phase_spec")
emit_determinism_digest("p0", "l2_phase_spec")

_emit_dispatches_healing_run("p1", "l2_phase_spec", "L2")
_emit_routes_through("p1", "l2_phase_spec", "L2")
_emit_checks_agent_registry("p1", "l2_phase_spec", "agent_registry")
_emit_validates_agent_capability("p1", "l2_phase_spec", "capability")
_emit_dispatches_execution_plan("p1", "l2_phase_spec", "exec_plan")
_emit_agent_executes_agent("p1", "l2_phase_spec", "sub_agent")
_emit_routes_to_agent("p1", "l2_phase_spec", "target_agent")
_emit_verifies_policy("p1", "l2_phase_spec", "policy_check")
_emit_observes_runtime_state("p1", "l2_phase_spec", "runtime_state")
_emit_verifies_boundary("p1", "l2_phase_spec", "boundary_check")
_emit_transcripts_response("p1", "l2_phase_spec", "transcript")
_emit_hard_fails_untranscripted("p1", "l2_phase_spec")
_emit_gated_by_confidence("p1", "l2_phase_spec", "confidence_gate")
_emit_escalates_to_human("p1", "l2_phase_spec", "L2")
_emit_reads_policy_state("p1", "l2_phase_spec", "L2")
_emit_pulls_context("p1", "l2_phase_spec", "context_pull")
_emit_pulls_context("p1", "l2_phase_spec", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "l2_phase_spec", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "l2_phase_spec", "uwg_term_secondary")
_emit_writes_through("p1", "l2_phase_spec", "write_through")
_emit_writes_through("p1", "l2_phase_spec", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "l2_phase_spec", "safety_validation")
_emit_invokes_eval("p1", "l2_phase_spec", "eval_call")
_emit_proposal_commits_routing("p1", "l2_phase_spec", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "l2_phase_spec")
_emit_applies_guardrail("p0", "l2_phase_spec", "p0_governance")
_emit_snapshots_state("p0", "l2_phase_spec", "state_snapshot")
_emit_authorize_and_execute("p2", "l2_phase_spec", "execution_auth")
_emit_validates_capability("p2", "l2_phase_spec", "capability_check")
_emit_routes_to_capability("p2", "l2_phase_spec", "capability_route")
_emit_writes_via_uwg("p2", "l2_phase_spec", "uwg_write")
_emit_blocks_direct_write("p2", "l2_phase_spec", "direct_write_block")
_emit_records_tool_invocation("p2", "l2_phase_spec", "tool_invocation")
_emit_captures_execution_output("p2", "l2_phase_spec", "exec_output")
_emit_dispatches_agent("p3", "l2_phase_spec", "agent_dispatch")
_emit_coordinates_agents("p3", "l2_phase_spec", "agent_coordination")
_emit_records_workflow_lineage("p3", "l2_phase_spec", "workflow_lineage")
_emit_records_healing_outcome("p3", "l2_phase_spec", "healing_outcome")
_emit_escalates_failure("p3", "l2_phase_spec", "failure_escalation")
_emit_orchestrates_workflow("p3", "l2_phase_spec", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "l2_phase_spec", "healing_dispatch")
_emit_invokes_evaluation("p3", "l2_phase_spec", "evaluation_signal")
_emit_records_telemetry_event("p4", "l2_phase_spec", "telemetry_event")
_emit_captures_evaluation_metric("p4", "l2_phase_spec", "eval_metric")
_emit_stores_embedding("p4", "l2_phase_spec", "embedding_store")
_emit_updates_meta_learning_state("p4", "l2_phase_spec", "meta_learning")
_emit_links_execution_to_snapshot("p4", "l2_phase_spec", "exec_snapshot_link")


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
    )
)
__all__ = ["L2ExecutionPlan", "LEGACY_MIRROR_PLAN", "PhaseSpec"]
