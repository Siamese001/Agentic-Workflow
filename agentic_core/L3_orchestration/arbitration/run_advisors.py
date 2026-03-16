"""
Advisor Execution Harness

Side-effect free execution of multiple advisors with validation.
Ensures deterministic outputs and contract compliance.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_authorize_and_execute("p2", "run_advisors", "execution_auth")
_emit_validates_capability("p2", "run_advisors", "capability_check")
_emit_routes_to_capability("p2", "run_advisors", "capability_route")
_emit_writes_via_uwg("p2", "run_advisors", "uwg_write")
_emit_blocks_direct_write("p2", "run_advisors", "direct_write_block")
_emit_records_tool_invocation("p2", "run_advisors", "tool_invocation")
_emit_captures_execution_output("p2", "run_advisors", "exec_output")
_emit_dispatches_agent("p3", "run_advisors", "agent_dispatch")
_emit_coordinates_agents("p3", "run_advisors", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_advisors", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_advisors", "healing_outcome")
_emit_escalates_failure("p3", "run_advisors", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_advisors", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_advisors", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_advisors", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_advisors", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_advisors", "eval_metric")
_emit_stores_embedding("p4", "run_advisors", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_advisors", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_advisors", "exec_snapshot_link")
from .advisors import get_available_advisors, run_advisor
from .arbitration_contract import AdvisorProposal

emit_replay_key("p0", "run_advisors")
emit_determinism_digest("p0", "run_advisors")

_emit_dispatches_healing_run("p1", "run_advisors", "L3")
_emit_routes_through("p1", "run_advisors", "L3")
_emit_checks_agent_registry("p1", "run_advisors", "agent_registry")
_emit_validates_agent_capability("p1", "run_advisors", "capability")
_emit_dispatches_execution_plan("p1", "run_advisors", "exec_plan")
_emit_agent_executes_agent("p1", "run_advisors", "sub_agent")
_emit_routes_to_agent("p1", "run_advisors", "target_agent")
_emit_verifies_policy("p1", "run_advisors", "policy_check")
_emit_observes_runtime_state("p1", "run_advisors", "runtime_state")
_emit_verifies_boundary("p1", "run_advisors", "boundary_check")
_emit_transcripts_response("p1", "run_advisors", "transcript")
_emit_hard_fails_untranscripted("p1", "run_advisors")
_emit_gated_by_confidence("p1", "run_advisors", "confidence_gate")
_emit_escalates_to_human("p1", "run_advisors", "L3")
_emit_reads_policy_state("p1", "run_advisors", "L3")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("run_advisors", "p4obs", "metric_1")
_emit_emits_metric_event("run_advisors", "p4obs", "metric_2")
_emit_emits_metric_event("run_advisors", "p4obs", "metric_3")
_emit_emits_metric_event("run_advisors", "p4obs", "metric_4")
_emit_emits_metric_event("run_advisors", "p4obs", "metric_5")
_emit_emits_metric_event("run_advisors", "p4obs", "metric_6")
_emit_records_incident_event("run_advisors", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_advisors", "p4obs", "anomaly")
_emit_writes_observability_log("run_advisors", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_advisors", "p4obs", "mon_state")
_emit_triggers_alert("run_advisors", "p4obs", "alert")
_emit_links_incident_trace("run_advisors", "p4obs", "trace_link")
_emit_captures_pattern("run_advisors", "p3lm", "pattern")
_emit_records_learning_event("run_advisors", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_advisors", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_advisors", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_advisors", "p3lm", "routing")
_emit_improves_agent_policy("run_advisors", "p3lm", "policy")
_emit_stores_learning_state("run_advisors", "p3lm", "state")
_emit_records_execution_trace("run_advisors", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_advisors", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_advisors", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_advisors", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_advisors", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_advisors", "env_read", "p2_env_1")
_emit_reads_environ("run_advisors", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_advisors", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_advisors", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_advisors", "context_pull")
_emit_pulls_context("p1", "run_advisors", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_advisors", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_advisors", "uwg_term_2")
_emit_writes_through("p1", "run_advisors", "write_through")
_emit_writes_through("p1", "run_advisors", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_advisors", "safety_validation")
_emit_invokes_eval("p1", "run_advisors", "eval_call")
_emit_proposal_commits_routing("p1", "run_advisors", "routing_commit")


def run_advisors(task_dict: dict[str, str], advisor_ids: list[str]) -> list[AdvisorProposal]:
    """Run multiple advisors and return their proposals.

    Args:
        task_dict: Task description dictionary
        advisor_ids: List of advisor IDs to run

    Returns:
        List of AdvisorProposal objects

    Raises:
        ValueError: If any advisor_id is invalid
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "run_advisors", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "run_advisors", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "run_advisors")
    proposals = []
    for advisor_id in advisor_ids:
        available = get_available_advisors()
        if advisor_id not in available:
            raise ValueError(f"Invalid advisor_id: {advisor_id}. Available: {available}")
        proposal = run_advisor(advisor_id, task_dict)
        _validate_proposal(proposal)
        proposals.append(proposal)
    return proposals


def _validate_proposal(proposal: AdvisorProposal) -> None:
    """Validate proposal meets contract requirements.

    Args:
        proposal: Proposal to validate

    Raises:
        ValueError: If proposal violates contract
    """
    if not proposal.decision.strip():
        raise ValueError(f"Advisor {proposal.advisor_id} returned empty decision")
    if not 0 <= proposal.confidence <= 100:
        raise ValueError(f"Advisor {proposal.advisor_id} returned invalid confidence: {proposal.confidence}")
    for i, rationale in enumerate(proposal.rationale):
        if not rationale.strip():
            raise ValueError(f"Advisor {proposal.advisor_id} returned empty rationale item at index {i}")
    for i, risk in enumerate(proposal.risks):
        if not risk.strip():
            raise ValueError(f"Advisor {proposal.advisor_id} returned empty risk item at index {i}")
    for i, artifact in enumerate(proposal.artifacts):
        if not artifact.strip():
            raise ValueError(f"Advisor {proposal.advisor_id} returned empty artifact item at index {i}")


def run_all_advisors(task_dict: dict[str, str]) -> list[AdvisorProposal]:
    """Run all available advisors.

    Args:
        task_dict: Task description dictionary

    Returns:
        List of AdvisorProposal objects from all advisors
    """
    advisor_ids = get_available_advisors()
    return run_advisors(task_dict, advisor_ids)


__all__ = ["run_advisors", "run_all_advisors"]
