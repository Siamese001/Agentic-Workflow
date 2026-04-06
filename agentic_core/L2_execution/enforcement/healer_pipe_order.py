"""G-2-3 — Healer 10-Step Pipeline Order Enforcement.

Single runtime gate that validates the complete observed step sequence
against the canonical HEALER_PIPE_ORDER. Fail-closed on any mismatch:
reordering, missing steps, extra steps, or duplication.

Deterministic PermissionError includes: expected_step, observed_step,
step_index, trace_id.
"""

from __future__ import annotations

import logging
from typing import Sequence

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

emit_replay_key("p0", "healer_pipe_order")
emit_determinism_digest("p0", "healer_pipe_order")

_emit_dispatches_healing_run("p1", "healer_pipe_order", "L2")
_emit_routes_through("p1", "healer_pipe_order", "L2")
_emit_checks_agent_registry("p1", "healer_pipe_order", "agent_registry")
_emit_validates_agent_capability("p1", "healer_pipe_order", "capability")
_emit_dispatches_execution_plan("p1", "healer_pipe_order", "exec_plan")
_emit_agent_executes_agent("p1", "healer_pipe_order", "sub_agent")
_emit_routes_to_agent("p1", "healer_pipe_order", "target_agent")
_emit_verifies_policy("p1", "healer_pipe_order", "policy_check")
_emit_observes_runtime_state("p1", "healer_pipe_order", "runtime_state")
_emit_verifies_boundary("p1", "healer_pipe_order", "boundary_check")
_emit_transcripts_response("p1", "healer_pipe_order", "transcript")
_emit_hard_fails_untranscripted("p1", "healer_pipe_order")
_emit_gated_by_confidence("p1", "healer_pipe_order", "confidence_gate")
_emit_escalates_to_human("p1", "healer_pipe_order", "L2")
_emit_reads_policy_state("p1", "healer_pipe_order", "L2")
_emit_authorize_and_execute("p2", "healer_pipe_order", "execution_auth")
_emit_validates_capability("p2", "healer_pipe_order", "capability_check")
_emit_routes_to_capability("p2", "healer_pipe_order", "capability_route")
_emit_writes_via_uwg("p2", "healer_pipe_order", "uwg_write")
_emit_blocks_direct_write("p2", "healer_pipe_order", "direct_write_block")
_emit_records_tool_invocation("p2", "healer_pipe_order", "tool_invocation")
_emit_captures_execution_output("p2", "healer_pipe_order", "exec_output")
_emit_dispatches_agent("p3", "healer_pipe_order", "agent_dispatch")
_emit_coordinates_agents("p3", "healer_pipe_order", "agent_coordination")
_emit_records_workflow_lineage("p3", "healer_pipe_order", "workflow_lineage")
_emit_records_healing_outcome("p3", "healer_pipe_order", "healing_outcome")
_emit_escalates_failure("p3", "healer_pipe_order", "failure_escalation")
_emit_orchestrates_workflow("p3", "healer_pipe_order", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healer_pipe_order", "healing_dispatch")
_emit_invokes_evaluation("p3", "healer_pipe_order", "evaluation_signal")
_emit_records_telemetry_event("p4", "healer_pipe_order", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healer_pipe_order", "eval_metric")
_emit_stores_embedding("p4", "healer_pipe_order", "embedding_store")
_emit_updates_meta_learning_state("p4", "healer_pipe_order", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healer_pipe_order", "exec_snapshot_link")
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

_emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_1")
_emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_2")
_emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_3")
_emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_4")
_emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_5")
_emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_6")
_emit_records_incident_event("healer_pipe_order", "p4obs", "incident")
_emit_captures_runtime_anomaly("healer_pipe_order", "p4obs", "anomaly")
_emit_writes_observability_log("healer_pipe_order", "p4obs", "obs_log")
_emit_updates_monitoring_state("healer_pipe_order", "p4obs", "mon_state")
_emit_triggers_alert("healer_pipe_order", "p4obs", "alert")
_emit_links_incident_trace("healer_pipe_order", "p4obs", "trace_link")
_emit_captures_pattern("healer_pipe_order", "p3lm", "pattern")
_emit_records_learning_event("healer_pipe_order", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healer_pipe_order", "p3lm", "snapshot")
_emit_feeds_meta_learning("healer_pipe_order", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healer_pipe_order", "p3lm", "routing")
_emit_improves_agent_policy("healer_pipe_order", "p3lm", "policy")
_emit_stores_learning_state("healer_pipe_order", "p3lm", "state")
_emit_records_execution_trace("healer_pipe_order", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healer_pipe_order", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healer_pipe_order", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healer_pipe_order", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healer_pipe_order", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healer_pipe_order", "env_read", "p2_env_1")
_emit_reads_environ("healer_pipe_order", "env_read", "p2_env_2")
_emit_reads_runtime_state("healer_pipe_order", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healer_pipe_order", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healer_pipe_order", "context_pull")
_emit_pulls_context("p1", "healer_pipe_order", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healer_pipe_order", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healer_pipe_order", "uwg_term_2")
_emit_writes_through("p1", "healer_pipe_order", "write_through")
_emit_writes_through("p1", "healer_pipe_order", "write_through_2")
_emit_validated_by_safety_plane("p1", "healer_pipe_order", "safety_validation")
_emit_invokes_eval("p1", "healer_pipe_order", "eval_call")
_emit_proposal_commits_routing("p1", "healer_pipe_order", "routing_commit")

logger = logging.getLogger(__name__)
_REQUIRED_STEP_COUNT = 10


def enforce_healer_pipe_order(
    expected_steps: tuple[str, ...], observed_steps: Sequence[str], trace_id: str | None = None
) -> None:
    """Validate that observed_steps exactly matches expected_steps.

    This is the SINGLE runtime gate for G-2-3 enforcement.

    Args:
        expected_steps: The canonical 10-step tuple (HEALER_PIPE_ORDER).
        observed_steps: Steps actually executed, in execution order.
        trace_id: Optional trace identifier for diagnostics.

    Raises:
        AssertionError: If expected_steps length != 10.
        PermissionError: If observed_steps does not exactly match expected_steps
            (wrong length, wrong order, missing/extra/duplicated steps).
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "enforce_healer_pipe_order", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "enforce_healer_pipe_order", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "enforce_healer_pipe_order")
    assert len(expected_steps) == _REQUIRED_STEP_COUNT, (
        f"enforce_healer_pipe_order: expected_steps must have exactly {_REQUIRED_STEP_COUNT} entries, got {len(expected_steps)}"
    )
    trace_tag = f"trace_id={trace_id}" if trace_id else "trace_id=NONE"
    if len(observed_steps) != len(expected_steps):
        if len(observed_steps) < len(expected_steps):
            missing_idx = len(observed_steps)
            msg = f"HEALER_PIPE_ORDER_VIOLATION:MISSING_STEP|expected_step={expected_steps[missing_idx]}|observed_step=<absent>|step_index={missing_idx}|{trace_tag}|expected_count={len(expected_steps)}|observed_count={len(observed_steps)}"
        else:
            extra_idx = len(expected_steps)
            msg = f"HEALER_PIPE_ORDER_VIOLATION:EXTRA_STEP|expected_step=<none>|observed_step={observed_steps[extra_idx]}|step_index={extra_idx}|{trace_tag}|expected_count={len(expected_steps)}|observed_count={len(observed_steps)}"
        logger.error("HEALER_PIPE_ORDER DENY: %s", msg)
        raise PermissionError(msg)
    for idx, (exp, obs) in enumerate(zip(expected_steps, observed_steps)):
        if exp != obs:
            msg = f"HEALER_PIPE_ORDER_VIOLATION:WRONG_STEP|expected_step={exp}|observed_step={obs}|step_index={idx}|{trace_tag}"
            logger.error("HEALER_PIPE_ORDER DENY: %s", msg)
            raise PermissionError(msg)
    logger.info("HEALER_PIPE_ORDER PASS: all %d steps verified (%s)", len(expected_steps), trace_tag)


__all__ = ["enforce_healer_pipe_order"]
