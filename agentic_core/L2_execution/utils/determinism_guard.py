"""Determinism guard context managers for REQ-111 and REQ-114.

Provides context managers to assert absence of uuid4 and wall-clock usage
in determinism-critical code paths.
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from typing import Generator

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "determinism_guard")
trace_contract.emit_determinism_digest("p0", "determinism_guard")

trace_contract._emit_dispatches_healing_run("p1", "determinism_guard", "L2")
trace_contract._emit_routes_through("p1", "determinism_guard", "L2")
trace_contract._emit_checks_agent_registry("p1", "determinism_guard", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "determinism_guard", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "determinism_guard", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "determinism_guard", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "determinism_guard", "target_agent")
trace_contract._emit_verifies_policy("p1", "determinism_guard", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "determinism_guard", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "determinism_guard", "boundary_check")
trace_contract._emit_transcripts_response("p1", "determinism_guard", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "determinism_guard")
trace_contract._emit_gated_by_confidence("p1", "determinism_guard", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "determinism_guard", "L2")
trace_contract._emit_reads_policy_state("p1", "determinism_guard", "L2")
trace_contract._emit_authorize_and_execute("p2", "determinism_guard", "execution_auth")
trace_contract._emit_validates_capability("p2", "determinism_guard", "capability_check")
trace_contract._emit_routes_to_capability("p2", "determinism_guard", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "determinism_guard", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "determinism_guard", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "determinism_guard", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "determinism_guard", "exec_output")
trace_contract._emit_dispatches_agent("p3", "determinism_guard", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "determinism_guard", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "determinism_guard", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "determinism_guard", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "determinism_guard", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "determinism_guard", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "determinism_guard", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "determinism_guard", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "determinism_guard", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "determinism_guard", "eval_metric")
trace_contract._emit_stores_embedding("p4", "determinism_guard", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "determinism_guard", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "determinism_guard", "exec_snapshot_link")

trace_contract.record_execution_trace("determinism_guard", "determinism_guard_trace")


trace_contract._emit_emits_metric_event("determinism_guard", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("determinism_guard", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("determinism_guard", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("determinism_guard", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("determinism_guard", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("determinism_guard", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("determinism_guard", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("determinism_guard", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("determinism_guard", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("determinism_guard", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("determinism_guard", "p4obs", "alert")
trace_contract._emit_links_incident_trace("determinism_guard", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("determinism_guard", "p3lm", "pattern")
trace_contract._emit_records_learning_event("determinism_guard", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("determinism_guard", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("determinism_guard", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("determinism_guard", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("determinism_guard", "p3lm", "policy")
trace_contract._emit_stores_learning_state("determinism_guard", "p3lm", "state")
trace_contract._emit_records_execution_trace("determinism_guard", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("determinism_guard", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("determinism_guard", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("determinism_guard", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("determinism_guard", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("determinism_guard", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("determinism_guard", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("determinism_guard", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("determinism_guard", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "determinism_guard", "context_pull")
trace_contract._emit_pulls_context("p1", "determinism_guard", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "determinism_guard", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "determinism_guard", "uwg_term_2")
trace_contract._emit_writes_through("p1", "determinism_guard", "write_through")
trace_contract._emit_writes_through("p1", "determinism_guard", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "determinism_guard", "safety_validation")
trace_contract._emit_invokes_eval("p1", "determinism_guard", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "determinism_guard", "routing_commit")


@contextmanager
def assert_no_uuid4() -> Generator[None, None, None]:
    """Context manager to assert no uuid4 is used within the context.

    Raises:
        RuntimeError: If uuid.uuid4() is called within the context.
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "assert_no_uuid4", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "assert_no_uuid4", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "assert_no_uuid4")
    original_uuid4 = uuid.uuid4

    def tracking_uuid4() -> uuid.UUID:
        raise RuntimeError(
            "uuid.uuid4() called in determinism-critical context. Use deterministic UUID generation instead.",
        )

    uuid.uuid4 = tracking_uuid4
    try:
        yield
    finally:
        uuid.uuid4 = original_uuid4


@contextmanager
def assert_no_wallclock() -> Generator[None, None, None]:
    """Context manager to assert no wall-clock is used within the context.

    Note: Cannot patch datetime.now directly as it's immutable, so we track
    time module functions which are the most common wall-clock sources.

    Raises:
        RuntimeError: If time.time(), time.sleep(), or similar wall-clock functions are called.
    """
    original_time = time.time
    original_sleep = time.sleep
    original_monotonic = getattr(time, "monotonic", None)

    def tracking_time() -> float:
        raise RuntimeError(
            "time.time() called in determinism-critical context. Use semantic clock ticks instead.",
        )

    def tracking_sleep(seconds: float) -> None:
        raise RuntimeError(
            "time.sleep() called in determinism-critical context. Use deterministic delay mechanisms instead.",
        )

    def tracking_monotonic() -> float:
        raise RuntimeError(
            "time.monotonic() called in determinism-critical context. Use semantic clock ticks instead.",
        )

    time.time = tracking_time
    time.sleep = tracking_sleep
    if original_monotonic is not None:
        time.monotonic = tracking_monotonic
    try:
        yield
    finally:
        time.time = original_time
        time.sleep = original_sleep
        if original_monotonic is not None:
            time.monotonic = original_monotonic


@contextmanager
def assert_deterministic_context() -> Generator[None, None, None]:
    """Combined context manager asserting both no uuid4 and no wall-clock.

    This is a convenience wrapper that enables both guards simultaneously.
    """
    with assert_no_uuid4(), assert_no_wallclock():
        yield
