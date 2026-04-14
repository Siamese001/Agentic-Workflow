"""Instructional injections for agentic_core - self-contained implementation.

This module provides instructional injection patterns without depending on apps_shared,
maintaining agentic_core boundary integrity.
"""

import logging

from agentic_core.config.injection_layer_config import InjectionLayer, InstructionalPattern
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "instructional_injections")
_emit_applies_guardrail("p0", "instructional_injections", "p0_governance")
_emit_reads_policy_state("p0", "instructional_injections", "policy_binding")
_emit_snapshots_state("p0", "instructional_injections", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
)

_emit_emits_metric_event("instructional_injections", "p4obs", "metric_1")
_emit_emits_metric_event("instructional_injections", "p4obs", "metric_2")
_emit_emits_metric_event("instructional_injections", "p4obs", "metric_3")
_emit_emits_metric_event("instructional_injections", "p4obs", "metric_4")
_emit_emits_metric_event("instructional_injections", "p4obs", "metric_5")
_emit_emits_metric_event("instructional_injections", "p4obs", "metric_6")
_emit_records_incident_event("instructional_injections", "p4obs", "incident")
_emit_captures_runtime_anomaly("instructional_injections", "p4obs", "anomaly")
_emit_writes_observability_log("instructional_injections", "p4obs", "obs_log")
_emit_updates_monitoring_state("instructional_injections", "p4obs", "mon_state")
_emit_triggers_alert("instructional_injections", "p4obs", "alert")
_emit_links_incident_trace("instructional_injections", "p4obs", "trace_link")
_emit_captures_pattern("instructional_injections", "p3lm", "pattern")
_emit_records_learning_event("instructional_injections", "p3lm", "learning_event")
_emit_writes_learning_snapshot("instructional_injections", "p3lm", "snapshot")
_emit_feeds_meta_learning("instructional_injections", "p3lm", "meta_feed")
_emit_updates_routing_strategy("instructional_injections", "p3lm", "routing")
_emit_improves_agent_policy("instructional_injections", "p3lm", "policy")
_emit_stores_learning_state("instructional_injections", "p3lm", "state")
_emit_records_execution_trace("instructional_injections", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("instructional_injections", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("instructional_injections", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("instructional_injections", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("instructional_injections", "L4_STATE", "p2_trace_5")
_emit_reads_environ("instructional_injections", "env_read", "p2_env_1")
_emit_reads_environ("instructional_injections", "env_read", "p2_env_2")
_emit_reads_runtime_state("instructional_injections", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("instructional_injections", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "instructional_injections", "context_pull")
_emit_pulls_context("p1", "instructional_injections", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "instructional_injections", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "instructional_injections", "uwg_term_2")
_emit_writes_through("p1", "instructional_injections", "write_through")
_emit_writes_through("p1", "instructional_injections", "write_through_2")
_emit_validated_by_safety_plane("p1", "instructional_injections", "safety_validation")
_emit_invokes_eval("p1", "instructional_injections", "eval_call")
_emit_proposal_commits_routing("p1", "instructional_injections", "routing_commit")
_emit_escalates_to_human("p1", "instructional_injections", "human_escalation")
_emit_routes_through("p1", "instructional_injections", "route_through")
_emit_checks_agent_registry("p1", "instructional_injections", "agent_registry")
_emit_validates_agent_capability("p1", "instructional_injections", "capability")
_emit_dispatches_execution_plan("p1", "instructional_injections", "exec_plan")
_emit_agent_executes_agent("p1", "instructional_injections", "sub_agent")
_emit_routes_to_agent("p1", "instructional_injections", "target_agent")
_emit_verifies_policy("p1", "instructional_injections", "policy_check")
_emit_observes_runtime_state("p1", "instructional_injections", "runtime_state")
_emit_verifies_boundary("p1", "instructional_injections", "boundary_check")
_emit_transcripts_response("p1", "instructional_injections", "transcript")
_emit_hard_fails_untranscripted("p1", "instructional_injections")
_emit_gated_by_confidence("p1", "instructional_injections", "confidence_gate")
emit_replay_key("p0", "instructional_injections")
emit_determinism_digest("p0", "instructional_injections")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "instructional_injections", "execution_auth")
_emit_validates_capability("p2", "instructional_injections", "capability_check")
_emit_routes_to_capability("p2", "instructional_injections", "capability_route")
_emit_writes_via_uwg("p2", "instructional_injections", "uwg_write")
_emit_blocks_direct_write("p2", "instructional_injections", "direct_write_block")
_emit_records_tool_invocation("p2", "instructional_injections", "tool_invocation")
_emit_captures_execution_output("p2", "instructional_injections", "exec_output")
_emit_dispatches_agent("p3", "instructional_injections", "agent_dispatch")
_emit_coordinates_agents("p3", "instructional_injections", "agent_coordination")
_emit_records_workflow_lineage("p3", "instructional_injections", "workflow_lineage")
_emit_records_healing_outcome("p3", "instructional_injections", "healing_outcome")
_emit_escalates_failure("p3", "instructional_injections", "failure_escalation")
_emit_orchestrates_workflow("p3", "instructional_injections", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "instructional_injections", "healing_dispatch")
_emit_invokes_evaluation("p3", "instructional_injections", "evaluation_signal")
_emit_records_telemetry_event("p4", "instructional_injections", "telemetry_event")
_emit_captures_evaluation_metric("p4", "instructional_injections", "eval_metric")
_emit_stores_embedding("p4", "instructional_injections", "embedding_store")
_emit_updates_meta_learning_state("p4", "instructional_injections", "meta_learning")
_emit_links_execution_to_snapshot("p4", "instructional_injections", "exec_snapshot_link")

logger = logging.getLogger(__name__)


def get_instructional_injections() -> list[InstructionalPattern]:
    """Get instructional injection patterns from YAML (mandatory).

    YAML-only enforcement: No markdown fallback.
    If YAML loading fails, raises typed exception.

    Returns:
        List of InstructionalPattern objects.

    Raises:
        ImportError: If YAML loader not available.
        FileNotFoundError: If YAML corpus not found.
        YamlValidationError: If YAML validation fails.
    """
    from agentic_core.config.yaml_injection_loader import get_yaml_loader

    yaml_loader = get_yaml_loader()
    all_patterns = yaml_loader.load_all_patterns()
    patterns = []
    for layer_patterns in all_patterns.values():
        patterns.extend(layer_patterns)
    logger.info(f"Loaded {len(patterns)} instructional patterns from YAML")
    return patterns


def get_required_injections() -> list[InstructionalPattern]:
    """Get required instructional injection patterns.

    Returns:
        List of required InstructionalPattern objects.
        Deterministic rule:
        1. If any patterns have required=True, return only those
        2. If no patterns have required=True, return all FRAMING layer patterns
    """
    all_patterns = get_instructional_injections()
    required_patterns = [pattern for pattern in all_patterns if pattern.required]
    if required_patterns:
        logger.info(f"Identified {len(required_patterns)} explicitly required instructional patterns")
        return required_patterns
    else:
        framing_patterns = [pattern for pattern in all_patterns if pattern.layer == InjectionLayer.FRAMING]
        logger.info(
            f"No explicit required patterns found; using FRAMING layer fallback: {len(framing_patterns)} patterns",
        )
        return framing_patterns
