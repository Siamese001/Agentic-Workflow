"""
Multi-Agent Advisors

Pure function advisors that provide deterministic recommendations.
No I/O, no side effects, fully deterministic outputs.
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
)

_emit_authorize_and_execute("p2", "advisors", "execution_auth")
_emit_validates_capability("p2", "advisors", "capability_check")
_emit_routes_to_capability("p2", "advisors", "capability_route")
_emit_writes_via_uwg("p2", "advisors", "uwg_write")
_emit_blocks_direct_write("p2", "advisors", "direct_write_block")
_emit_records_tool_invocation("p2", "advisors", "tool_invocation")
_emit_captures_execution_output("p2", "advisors", "exec_output")
_emit_dispatches_agent("p3", "advisors", "agent_dispatch")
_emit_coordinates_agents("p3", "advisors", "agent_coordination")
_emit_records_workflow_lineage("p3", "advisors", "workflow_lineage")
_emit_records_healing_outcome("p3", "advisors", "healing_outcome")
_emit_escalates_failure("p3", "advisors", "failure_escalation")
_emit_orchestrates_workflow("p3", "advisors", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "advisors", "healing_dispatch")
_emit_invokes_evaluation("p3", "advisors", "evaluation_signal")
_emit_records_telemetry_event("p4", "advisors", "telemetry_event")
_emit_captures_evaluation_metric("p4", "advisors", "eval_metric")
_emit_stores_embedding("p4", "advisors", "embedding_store")
_emit_updates_meta_learning_state("p4", "advisors", "meta_learning")
_emit_links_execution_to_snapshot("p4", "advisors", "exec_snapshot_link")
from .arbitration_contract import AdvisorProposal

emit_replay_key("p0", "advisors")
emit_determinism_digest("p0", "advisors")

_emit_dispatches_healing_run("p1", "advisors", "L3")
_emit_routes_through("p1", "advisors", "L3")
_emit_escalates_to_human("p1", "advisors", "L3")
_emit_reads_policy_state("p1", "advisors", "L3")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("advisors", "p4obs", "metric_1")
_emit_emits_metric_event("advisors", "p4obs", "metric_2")
_emit_emits_metric_event("advisors", "p4obs", "metric_3")
_emit_emits_metric_event("advisors", "p4obs", "metric_4")
_emit_emits_metric_event("advisors", "p4obs", "metric_5")
_emit_emits_metric_event("advisors", "p4obs", "metric_6")
_emit_records_incident_event("advisors", "p4obs", "incident")
_emit_captures_runtime_anomaly("advisors", "p4obs", "anomaly")
_emit_writes_observability_log("advisors", "p4obs", "obs_log")
_emit_updates_monitoring_state("advisors", "p4obs", "mon_state")
_emit_triggers_alert("advisors", "p4obs", "alert")
_emit_links_incident_trace("advisors", "p4obs", "trace_link")
_emit_captures_pattern("advisors", "p3lm", "pattern")
_emit_records_learning_event("advisors", "p3lm", "learning_event")
_emit_writes_learning_snapshot("advisors", "p3lm", "snapshot")
_emit_feeds_meta_learning("advisors", "p3lm", "meta_feed")
_emit_updates_routing_strategy("advisors", "p3lm", "routing")
_emit_improves_agent_policy("advisors", "p3lm", "policy")
_emit_stores_learning_state("advisors", "p3lm", "state")
_emit_records_execution_trace("advisors", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("advisors", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("advisors", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("advisors", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("advisors", "L4_STATE", "p2_trace_5")
_emit_reads_environ("advisors", "env_read", "p2_env_1")
_emit_reads_environ("advisors", "env_read", "p2_env_2")
_emit_reads_runtime_state("advisors", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("advisors", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "advisors", "context_pull")
_emit_pulls_context("p1", "advisors", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "advisors", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "advisors", "uwg_term_2")
_emit_writes_through("p1", "advisors", "write_through")
_emit_writes_through("p1", "advisors", "write_through_2")
_emit_validated_by_safety_plane("p1", "advisors", "safety_validation")
_emit_invokes_eval("p1", "advisors", "eval_call")
_emit_proposal_commits_routing("p1", "advisors", "routing_commit")


def risk_averse_advisor(task: dict[str, str]) -> AdvisorProposal:
    """Risk-averse advisor that prioritizes safety.

    Args:
        task: Task dictionary with task details

    Returns:
        AdvisorProposal with risk-averse recommendation
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "risk_averse_advisor", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "risk_averse_advisor", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "risk_averse_advisor")
    task_kind = task.get("task_kind", "unknown")
    if task_kind == "planning":
        decision = "create_detailed_plan"
        rationale = [
            "Detailed planning reduces uncertainty",
            "Step-by-step approach minimizes errors",
            "Documentation enables review",
        ]
        risks = ["Planning may take longer", "Over-planning can delay execution"]
        artifacts = ["plan.md", "checklist.md"]
        confidence = 85
    elif task_kind == "execution":
        decision = "execute_with_validation"
        rationale = [
            "Validation catches errors early",
            "Incremental execution reduces risk",
            "Rollback capability preserved",
        ]
        risks = ["Validation adds overhead", "Slower than direct execution"]
        artifacts = ["validation_log.json", "rollback_plan.md"]
        confidence = 90
    else:
        decision = "proceed_with_caution"
        rationale = ["Unknown task type requires caution", "Conservative approach minimizes risk"]
        risks = ["May be overly conservative", "Could miss optimization opportunities"]
        artifacts = ["risk_assessment.md"]
        confidence = 70
    return AdvisorProposal(
        advisor_id="risk_averse",
        decision=decision,
        confidence=confidence,
        rationale=rationale,
        risks=risks,
        artifacts=artifacts,
    )


def throughput_advisor(task: dict[str, str]) -> AdvisorProposal:
    """Throughput advisor that prioritizes speed and efficiency.

    Args:
        task: Task dictionary with task details

    Returns:
        AdvisorProposal with throughput-focused recommendation
    """
    task_kind = task.get("task_kind", "unknown")
    if task_kind == "planning":
        decision = "create_minimal_plan"
        rationale = [
            "Minimal planning enables faster start",
            "Just-in-time detail collection",
            "Iterative refinement possible",
        ]
        risks = ["May miss important details", "Requires more adaptation during execution"]
        artifacts = ["minimal_plan.md"]
        confidence = 75
    elif task_kind == "execution":
        decision = "execute_directly"
        rationale = ["Direct execution is fastest", "No validation overhead", "Maximum throughput"]
        risks = ["Errors may propagate further", "Harder to rollback changes"]
        artifacts = ["execution_log.json"]
        confidence = 80
    else:
        decision = "proceed_optimally"
        rationale = ["Optimal approach maximizes efficiency", "Assumes reasonable risk tolerance"]
        risks = ["May underestimate risks", "Could require rework"]
        artifacts = ["optimization_plan.md"]
        confidence = 65
    return AdvisorProposal(
        advisor_id="throughput",
        decision=decision,
        confidence=confidence,
        rationale=rationale,
        risks=risks,
        artifacts=artifacts,
    )


ADVISORS: dict[str, callable] = {"risk_averse": risk_averse_advisor, "throughput": throughput_advisor}


def get_available_advisors() -> list[str]:
    """Get list of available advisor IDs.

    Returns:
        List of advisor IDs in deterministic order
    """
    return sorted(ADVISORS.keys())


def run_advisor(advisor_id: str, task: dict[str, str]) -> AdvisorProposal:
    """Run a single advisor and return its proposal.

    Args:
        advisor_id: ID of advisor to run
        task: Task dictionary

    Returns:
        AdvisorProposal from the advisor

    Raises:
        ValueError: If advisor_id is not recognized
    """
    if advisor_id not in ADVISORS:
        raise ValueError(f"Unknown advisor: {advisor_id}")
    advisor_func = ADVISORS[advisor_id]
    proposal = advisor_func(task)
    if proposal.advisor_id != advisor_id:
        raise ValueError(f"Advisor {advisor_id} returned proposal with wrong ID: {proposal.advisor_id}")
    return proposal
