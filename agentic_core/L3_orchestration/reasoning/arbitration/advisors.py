"""
Multi-Agent Advisors

Pure function advisors that provide deterministic recommendations.
No I/O, no side effects, fully deterministic outputs.
"""

from __future__ import annotations

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

from .arbitration_contract import AdvisorProposal

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
    _emit_records_execution_trace,
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
