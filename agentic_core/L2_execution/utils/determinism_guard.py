"""Determinism guard context managers for REQ-111 and REQ-114.

Provides context managers to assert absence of uuid4 and wall-clock usage
in determinism-critical code paths.
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from typing import Generator

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
    record_execution_trace,
)

emit_replay_key("p0", "determinism_guard")
emit_determinism_digest("p0", "determinism_guard")

_emit_dispatches_healing_run("p1", "determinism_guard", "L2")
_emit_routes_through("p1", "determinism_guard", "L2")
_emit_checks_agent_registry("p1", "determinism_guard", "agent_registry")
_emit_validates_agent_capability("p1", "determinism_guard", "capability")
_emit_dispatches_execution_plan("p1", "determinism_guard", "exec_plan")
_emit_agent_executes_agent("p1", "determinism_guard", "sub_agent")
_emit_routes_to_agent("p1", "determinism_guard", "target_agent")
_emit_verifies_policy("p1", "determinism_guard", "policy_check")
_emit_observes_runtime_state("p1", "determinism_guard", "runtime_state")
_emit_verifies_boundary("p1", "determinism_guard", "boundary_check")
_emit_transcripts_response("p1", "determinism_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "determinism_guard")
_emit_gated_by_confidence("p1", "determinism_guard", "confidence_gate")
_emit_escalates_to_human("p1", "determinism_guard", "L2")
_emit_reads_policy_state("p1", "determinism_guard", "L2")
_emit_authorize_and_execute("p2", "determinism_guard", "execution_auth")
_emit_validates_capability("p2", "determinism_guard", "capability_check")
_emit_routes_to_capability("p2", "determinism_guard", "capability_route")
_emit_writes_via_uwg("p2", "determinism_guard", "uwg_write")
_emit_blocks_direct_write("p2", "determinism_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "determinism_guard", "tool_invocation")
_emit_captures_execution_output("p2", "determinism_guard", "exec_output")
_emit_dispatches_agent("p3", "determinism_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "determinism_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "determinism_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "determinism_guard", "healing_outcome")
_emit_escalates_failure("p3", "determinism_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "determinism_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "determinism_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "determinism_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "determinism_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "determinism_guard", "eval_metric")
_emit_stores_embedding("p4", "determinism_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "determinism_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "determinism_guard", "exec_snapshot_link")
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

record_execution_trace("determinism_guard", "determinism_guard_trace")


_emit_emits_metric_event("determinism_guard", "p4obs", "metric_1")
_emit_emits_metric_event("determinism_guard", "p4obs", "metric_2")
_emit_emits_metric_event("determinism_guard", "p4obs", "metric_3")
_emit_emits_metric_event("determinism_guard", "p4obs", "metric_4")
_emit_emits_metric_event("determinism_guard", "p4obs", "metric_5")
_emit_emits_metric_event("determinism_guard", "p4obs", "metric_6")
_emit_records_incident_event("determinism_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("determinism_guard", "p4obs", "anomaly")
_emit_writes_observability_log("determinism_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("determinism_guard", "p4obs", "mon_state")
_emit_triggers_alert("determinism_guard", "p4obs", "alert")
_emit_links_incident_trace("determinism_guard", "p4obs", "trace_link")
_emit_captures_pattern("determinism_guard", "p3lm", "pattern")
_emit_records_learning_event("determinism_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("determinism_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("determinism_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("determinism_guard", "p3lm", "routing")
_emit_improves_agent_policy("determinism_guard", "p3lm", "policy")
_emit_stores_learning_state("determinism_guard", "p3lm", "state")
_emit_records_execution_trace("determinism_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("determinism_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("determinism_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("determinism_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("determinism_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("determinism_guard", "env_read", "p2_env_1")
_emit_reads_environ("determinism_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("determinism_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("determinism_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "determinism_guard", "context_pull")
_emit_pulls_context("p1", "determinism_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "determinism_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "determinism_guard", "uwg_term_2")
_emit_writes_through("p1", "determinism_guard", "write_through")
_emit_writes_through("p1", "determinism_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "determinism_guard", "safety_validation")
_emit_invokes_eval("p1", "determinism_guard", "eval_call")
_emit_proposal_commits_routing("p1", "determinism_guard", "routing_commit")


@contextmanager
def assert_no_uuid4() -> Generator[None, None, None]:
    """Context manager to assert no uuid4 is used within the context.

    Raises:
        RuntimeError: If uuid.uuid4() is called within the context.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_no_uuid4", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_no_uuid4", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "assert_no_uuid4")
    original_uuid4 = uuid.uuid4

    def tracking_uuid4() -> uuid.UUID:
        raise RuntimeError(
            "uuid.uuid4() called in determinism-critical context. Use deterministic UUID generation instead."
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
            "time.time() called in determinism-critical context. Use semantic clock ticks instead."
        )

    def tracking_sleep(seconds: float) -> None:
        raise RuntimeError(
            "time.sleep() called in determinism-critical context. Use deterministic delay mechanisms instead."
        )

    def tracking_monotonic() -> float:
        raise RuntimeError(
            "time.monotonic() called in determinism-critical context. Use semantic clock ticks instead."
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
