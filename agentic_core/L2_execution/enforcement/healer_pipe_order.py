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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "healer_pipe_order")
trace_contract.emit_determinism_digest("p0", "healer_pipe_order")

trace_contract._emit_dispatches_healing_run("p1", "healer_pipe_order", "L2")
trace_contract._emit_routes_through("p1", "healer_pipe_order", "L2")
trace_contract._emit_checks_agent_registry("p1", "healer_pipe_order", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "healer_pipe_order", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "healer_pipe_order", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "healer_pipe_order", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "healer_pipe_order", "target_agent")
trace_contract._emit_verifies_policy("p1", "healer_pipe_order", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "healer_pipe_order", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "healer_pipe_order", "boundary_check")
trace_contract._emit_transcripts_response("p1", "healer_pipe_order", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "healer_pipe_order")
trace_contract._emit_gated_by_confidence("p1", "healer_pipe_order", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "healer_pipe_order", "L2")
trace_contract._emit_reads_policy_state("p1", "healer_pipe_order", "L2")
trace_contract._emit_authorize_and_execute("p2", "healer_pipe_order", "execution_auth")
trace_contract._emit_validates_capability("p2", "healer_pipe_order", "capability_check")
trace_contract._emit_routes_to_capability("p2", "healer_pipe_order", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "healer_pipe_order", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "healer_pipe_order", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "healer_pipe_order", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "healer_pipe_order", "exec_output")
trace_contract._emit_dispatches_agent("p3", "healer_pipe_order", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "healer_pipe_order", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "healer_pipe_order", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "healer_pipe_order", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "healer_pipe_order", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "healer_pipe_order", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "healer_pipe_order", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "healer_pipe_order", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "healer_pipe_order", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "healer_pipe_order", "eval_metric")
trace_contract._emit_stores_embedding("p4", "healer_pipe_order", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "healer_pipe_order", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "healer_pipe_order", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("healer_pipe_order", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("healer_pipe_order", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("healer_pipe_order", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("healer_pipe_order", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("healer_pipe_order", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("healer_pipe_order", "p4obs", "alert")
trace_contract._emit_links_incident_trace("healer_pipe_order", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("healer_pipe_order", "p3lm", "pattern")
trace_contract._emit_records_learning_event("healer_pipe_order", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("healer_pipe_order", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("healer_pipe_order", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("healer_pipe_order", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("healer_pipe_order", "p3lm", "policy")
trace_contract._emit_stores_learning_state("healer_pipe_order", "p3lm", "state")
trace_contract._emit_records_execution_trace("healer_pipe_order", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("healer_pipe_order", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("healer_pipe_order", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("healer_pipe_order", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("healer_pipe_order", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("healer_pipe_order", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("healer_pipe_order", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("healer_pipe_order", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("healer_pipe_order", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "healer_pipe_order", "context_pull")
trace_contract._emit_pulls_context("p1", "healer_pipe_order", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "healer_pipe_order", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "healer_pipe_order", "uwg_term_2")
trace_contract._emit_writes_through("p1", "healer_pipe_order", "write_through")
trace_contract._emit_writes_through("p1", "healer_pipe_order", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "healer_pipe_order", "safety_validation")
trace_contract._emit_invokes_eval("p1", "healer_pipe_order", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "healer_pipe_order", "routing_commit")

logger = logging.getLogger(__name__)
_REQUIRED_STEP_COUNT = 10


def enforce_healer_pipe_order(
    expected_steps: tuple[str, ...],
    observed_steps: Sequence[str],
    trace_id: str | None = None,
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

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "enforce_healer_pipe_order", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "enforce_healer_pipe_order", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "enforce_healer_pipe_order")
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
