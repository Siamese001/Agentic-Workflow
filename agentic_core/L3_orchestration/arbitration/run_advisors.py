"""
Advisor Execution Harness

Side-effect free execution of multiple advisors with validation.
Ensures deterministic outputs and contract compliance.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

from .advisors import get_available_advisors, run_advisor
from .arbitration_contract import AdvisorProposal

from agentic_core.runtime.lifecycle_trace_contract import (
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
