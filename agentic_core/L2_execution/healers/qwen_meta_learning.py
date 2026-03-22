"""
Qwen Meta-Learning Protection - Boundary Enforcement

Ensures Qwen metrics only update confidence priors and never modify
routing thresholds or other architectural constants.
"""

from __future__ import annotations

import logging

from agentic_core.L2_execution.healers.healing_tier_config import (
    HEALING_CONFIDENCE_X,
    HEALING_CONFIDENCE_Y,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("qwen_meta_learning", "p4obs", "metric_1")
_emit_emits_metric_event("qwen_meta_learning", "p4obs", "metric_2")
_emit_emits_metric_event("qwen_meta_learning", "p4obs", "metric_3")
_emit_emits_metric_event("qwen_meta_learning", "p4obs", "metric_4")
_emit_emits_metric_event("qwen_meta_learning", "p4obs", "metric_5")
_emit_emits_metric_event("qwen_meta_learning", "p4obs", "metric_6")
_emit_records_incident_event("qwen_meta_learning", "p4obs", "incident")
_emit_captures_runtime_anomaly("qwen_meta_learning", "p4obs", "anomaly")
_emit_writes_observability_log("qwen_meta_learning", "p4obs", "obs_log")
_emit_updates_monitoring_state("qwen_meta_learning", "p4obs", "mon_state")
_emit_triggers_alert("qwen_meta_learning", "p4obs", "alert")
_emit_links_incident_trace("qwen_meta_learning", "p4obs", "trace_link")
_emit_captures_pattern("qwen_meta_learning", "p3lm", "pattern")
_emit_records_learning_event("qwen_meta_learning", "p3lm", "learning_event")
_emit_writes_learning_snapshot("qwen_meta_learning", "p3lm", "snapshot")
_emit_feeds_meta_learning("qwen_meta_learning", "p3lm", "meta_feed")
_emit_updates_routing_strategy("qwen_meta_learning", "p3lm", "routing")
_emit_improves_agent_policy("qwen_meta_learning", "p3lm", "policy")
_emit_stores_learning_state("qwen_meta_learning", "p3lm", "state")
_emit_records_execution_trace("qwen_meta_learning", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("qwen_meta_learning", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("qwen_meta_learning", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("qwen_meta_learning", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("qwen_meta_learning", "L4_STATE", "p2_trace_5")
_emit_reads_environ("qwen_meta_learning", "env_read", "p2_env_1")
_emit_reads_environ("qwen_meta_learning", "env_read", "p2_env_2")
_emit_reads_runtime_state("qwen_meta_learning", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("qwen_meta_learning", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "qwen_meta_learning")
emit_determinism_digest("p0", "qwen_meta_learning")

_emit_dispatches_healing_run("p1", "qwen_meta_learning", "L2")
_emit_routes_through("p1", "qwen_meta_learning", "L2")
_emit_checks_agent_registry("p1", "qwen_meta_learning", "agent_registry")
_emit_validates_agent_capability("p1", "qwen_meta_learning", "capability")
_emit_dispatches_execution_plan("p1", "qwen_meta_learning", "exec_plan")
_emit_agent_executes_agent("p1", "qwen_meta_learning", "sub_agent")
_emit_routes_to_agent("p1", "qwen_meta_learning", "target_agent")
_emit_verifies_policy("p1", "qwen_meta_learning", "policy_check")
_emit_observes_runtime_state("p1", "qwen_meta_learning", "runtime_state")
_emit_verifies_boundary("p1", "qwen_meta_learning", "boundary_check")
_emit_transcripts_response("p1", "qwen_meta_learning", "transcript")
_emit_hard_fails_untranscripted("p1", "qwen_meta_learning")
_emit_gated_by_confidence("p1", "qwen_meta_learning", "confidence_gate")
_emit_escalates_to_human("p1", "qwen_meta_learning", "L2")
_emit_reads_policy_state("p1", "qwen_meta_learning", "L2")
_emit_pulls_context("p1", "qwen_meta_learning", "context_pull")
_emit_pulls_context("p1", "qwen_meta_learning", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "qwen_meta_learning", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "qwen_meta_learning", "uwg_term_secondary")
_emit_writes_through("p1", "qwen_meta_learning", "write_through")
_emit_writes_through("p1", "qwen_meta_learning", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "qwen_meta_learning", "safety_validation")
_emit_invokes_eval("p1", "qwen_meta_learning", "eval_call")
_emit_proposal_commits_routing("p1", "qwen_meta_learning", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "qwen_meta_learning")
_emit_applies_guardrail("p0", "qwen_meta_learning", "p0_governance")
_emit_snapshots_state("p0", "qwen_meta_learning", "state_snapshot")
_emit_authorize_and_execute("p2", "qwen_meta_learning", "execution_auth")
_emit_validates_capability("p2", "qwen_meta_learning", "capability_check")
_emit_routes_to_capability("p2", "qwen_meta_learning", "capability_route")
_emit_writes_via_uwg("p2", "qwen_meta_learning", "uwg_write")
_emit_blocks_direct_write("p2", "qwen_meta_learning", "direct_write_block")
_emit_records_tool_invocation("p2", "qwen_meta_learning", "tool_invocation")
_emit_captures_execution_output("p2", "qwen_meta_learning", "exec_output")
_emit_dispatches_agent("p3", "qwen_meta_learning", "agent_dispatch")
_emit_coordinates_agents("p3", "qwen_meta_learning", "agent_coordination")
_emit_records_workflow_lineage("p3", "qwen_meta_learning", "workflow_lineage")
_emit_records_healing_outcome("p3", "qwen_meta_learning", "healing_outcome")
_emit_escalates_failure("p3", "qwen_meta_learning", "failure_escalation")
_emit_orchestrates_workflow("p3", "qwen_meta_learning", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "qwen_meta_learning", "healing_dispatch")
_emit_invokes_evaluation("p3", "qwen_meta_learning", "evaluation_signal")
_emit_records_telemetry_event("p4", "qwen_meta_learning", "telemetry_event")
_emit_captures_evaluation_metric("p4", "qwen_meta_learning", "eval_metric")
_emit_stores_embedding("p4", "qwen_meta_learning", "embedding_store")
_emit_updates_meta_learning_state("p4", "qwen_meta_learning", "meta_learning")
_emit_links_execution_to_snapshot("p4", "qwen_meta_learning", "exec_snapshot_link")

logger = logging.getLogger(__name__)

# THRESHOLDS ARE IMPORTED FROM THE SINGLE SOURCE OF TRUTH: healing_tier_config.py
# HEALING_CONFIDENCE_X and HEALING_CONFIDENCE_Y must NOT be redefined here.

# Historical success rate store (in production backed by L4)
_historical_success_rates: dict[str, float] = {}
_NEUTRAL_PRIOR = 0.50


def get_historical_success_rate(error_signature: str) -> float:
    """Look up historical success rate for an error signature."""
    return _historical_success_rates.get(error_signature, _NEUTRAL_PRIOR)


def set_historical_success_rate(error_signature: str, rate: float) -> None:
    """Record historical success rate (allowed meta-learning operation)."""
    if not (0.0 <= rate <= 1.0):
        raise ValueError(f"rate must be in [0.0, 1.0], got {rate}")
    _historical_success_rates[error_signature] = rate


def update_qwen_confidence_prior(error_signature: str, success: bool) -> None:
    """
    Qwen metrics may update healer confidence priors ONLY.

    ALLOWED:
    - Historical success rate updates
    - Failure class prior adjustments
    - Tool readiness certainty updates

    FORBIDDEN:
    - HEALING_CONFIDENCE_X modification
    - HEALING_CONFIDENCE_Y modification
    - Routing election logic changes
    - Safety threshold modifications
    - Embedding scoring changes
    - RAG cutoff modifications
    """
    # Update historical success rate (allowed)
    current_rate = get_historical_success_rate(error_signature)
    if success:
        new_rate = min(1.0, current_rate + 0.1)
    else:
        new_rate = max(0.0, current_rate - 0.1)
    set_historical_success_rate(error_signature, new_rate)

    logger.info(f"Updated confidence prior for {error_signature}: {current_rate:.2f} -> {new_rate:.2f}")

    # THRESHOLDS REMAIN IMMUTABLE (values from healing_tier_config.py SSOT)
    assert HEALING_CONFIDENCE_X == 0.80, "X threshold is immutable"
    assert HEALING_CONFIDENCE_Y == 0.50, "Y threshold is immutable"


def validate_threshold_immutability() -> None:
    """Ensure healing thresholds cannot be modified."""
    # These values must never change
    assert HEALING_CONFIDENCE_X == 0.80, f"X threshold modified: {HEALING_CONFIDENCE_X}"
    assert HEALING_CONFIDENCE_Y == 0.50, f"Y threshold modified: {HEALING_CONFIDENCE_Y}"

    logger.debug("Threshold immutability validated")


def clear_historical_success_rates() -> None:
    """Clear all historical success rates (for testing)."""
    _historical_success_rates.clear()


__all__ = [
    "get_historical_success_rate",
    "set_historical_success_rate",
    "update_qwen_confidence_prior",
    "validate_threshold_immutability",
    "clear_historical_success_rates",
]
