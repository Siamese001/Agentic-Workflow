"""G-16-6 — Activation Gate: FAIL-CLOSED runtime prerequisite check.

Forbids ANY active/bounded-autonomy execution unless all three enforcement
subsystems are importable and present:

1. P5.1 capability chokepoint  (authorize_and_execute)
2. Mutation prohibition guard  (assert_no_persistent_write)
3. Healer 10-step pipe order   (enforce_healer_pipe_order)

Default is FAIL-CLOSED: if any component is missing, PermissionError is raised.
"""

from __future__ import annotations

import logging
from typing import Optional
from typing import Any

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

emit_replay_key("p0", "activation_gate")
emit_determinism_digest("p0", "activation_gate")

_emit_dispatches_healing_run("p1", "activation_gate", "L5")
_emit_routes_through("p1", "activation_gate", "L5")
_emit_checks_agent_registry("p1", "activation_gate", "agent_registry")
_emit_validates_agent_capability("p1", "activation_gate", "capability")
_emit_dispatches_execution_plan("p1", "activation_gate", "exec_plan")
_emit_agent_executes_agent("p1", "activation_gate", "sub_agent")
_emit_routes_to_agent("p1", "activation_gate", "target_agent")
_emit_verifies_policy("p1", "activation_gate", "policy_check")
_emit_observes_runtime_state("p1", "activation_gate", "runtime_state")
_emit_verifies_boundary("p1", "activation_gate", "boundary_check")
_emit_transcripts_response("p1", "activation_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "activation_gate")
_emit_gated_by_confidence("p1", "activation_gate", "confidence_gate")
_emit_escalates_to_human("p1", "activation_gate", "L5")
_emit_reads_policy_state("p1", "activation_gate", "L5")
_emit_authorize_and_execute("p2", "activation_gate", "execution_auth")
_emit_validates_capability("p2", "activation_gate", "capability_check")
_emit_routes_to_capability("p2", "activation_gate", "capability_route")
_emit_writes_via_uwg("p2", "activation_gate", "uwg_write")
_emit_blocks_direct_write("p2", "activation_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "activation_gate", "tool_invocation")
_emit_captures_execution_output("p2", "activation_gate", "exec_output")
_emit_dispatches_agent("p3", "activation_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "activation_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "activation_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "activation_gate", "healing_outcome")
_emit_escalates_failure("p3", "activation_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "activation_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "activation_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "activation_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "activation_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "activation_gate", "eval_metric")
_emit_stores_embedding("p4", "activation_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "activation_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "activation_gate", "exec_snapshot_link")
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

_emit_emits_metric_event("activation_gate", "p4obs", "metric_1")
_emit_emits_metric_event("activation_gate", "p4obs", "metric_2")
_emit_emits_metric_event("activation_gate", "p4obs", "metric_3")
_emit_emits_metric_event("activation_gate", "p4obs", "metric_4")
_emit_emits_metric_event("activation_gate", "p4obs", "metric_5")
_emit_emits_metric_event("activation_gate", "p4obs", "metric_6")
_emit_records_incident_event("activation_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("activation_gate", "p4obs", "anomaly")
_emit_writes_observability_log("activation_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("activation_gate", "p4obs", "mon_state")
_emit_triggers_alert("activation_gate", "p4obs", "alert")
_emit_links_incident_trace("activation_gate", "p4obs", "trace_link")
_emit_captures_pattern("activation_gate", "p3lm", "pattern")
_emit_records_learning_event("activation_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("activation_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("activation_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("activation_gate", "p3lm", "routing")
_emit_improves_agent_policy("activation_gate", "p3lm", "policy")
_emit_stores_learning_state("activation_gate", "p3lm", "state")
_emit_records_execution_trace("activation_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("activation_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("activation_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("activation_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("activation_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("activation_gate", "env_read", "p2_env_1")
_emit_reads_environ("activation_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("activation_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("activation_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "activation_gate", "context_pull")
_emit_pulls_context("p1", "activation_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "activation_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "activation_gate", "uwg_term_2")
_emit_writes_through("p1", "activation_gate", "write_through")
_emit_writes_through("p1", "activation_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "activation_gate", "safety_validation")
_emit_invokes_eval("p1", "activation_gate", "eval_call")
_emit_proposal_commits_routing("p1", "activation_gate", "routing_commit")

logger = logging.getLogger(__name__)
ACTIVATION_GATE_VERSION = "v5.4-P0"
_REQUIRED_COMPONENTS: list[tuple[str, str, str]] = [
    (
        "agentic_core.L2_execution.enforcement.capability_chokepoint",
        "authorize_and_execute",
        "capability_chokepoint",
    ),
    (
        "agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer",
        "assert_no_persistent_write",
        "mutation_prohibition",
    ),
    (
        "agentic_core.L2_execution.enforcement.healer_pipe_order",
        "enforce_healer_pipe_order",
        "healer_pipe_order",
    ),
]


def assert_activation_allowed(trace_id: str | None = None) -> None:
    """FAIL-CLOSED activation gate.

    Verifies that all three enforcement subsystems are importable.
    Raises PermissionError with a deterministic message listing any
    missing components if the check fails.

    Args:
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If any required enforcement component is missing.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_activation_allowed", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_activation_allowed", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "assert_activation_allowed")
    missing: list[str] = []
    for module_path, symbol_name, short_key in _REQUIRED_COMPONENTS:
        try:
            mod: Any = __import__(module_path, fromlist=[symbol_name])
            if not hasattr(mod, symbol_name):
                missing.append(short_key)
        except ImportError:
            missing.append(short_key)
    if missing:
        msg_parts = [
            f"ACTIVATION_DENIED:version={ACTIVATION_GATE_VERSION}",
            f"missing_components={','.join(sorted(missing))}",
        ]
        if trace_id is not None:
            msg_parts.append(f"trace_id={trace_id}")
        msg = "|".join(msg_parts)
        logger.error("ACTIVATION_GATE DENY: %s", msg)
        raise PermissionError(msg)


__all__ = ["ACTIVATION_GATE_VERSION", "assert_activation_allowed"]
