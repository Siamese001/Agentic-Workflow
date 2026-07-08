"""Instructional injections for agentic_core - self-contained implementation.

This module provides instructional injection patterns without depending on apps_shared,
maintaining agentic_core boundary integrity.
"""

import logging

from agentic_core.config.injection_layer_config import InjectionLayer, InstructionalPattern
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_records_execution_trace("p0", "evidence", "instructional_injections")
trace_contract._emit_applies_guardrail("p0", "instructional_injections", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "instructional_injections", "policy_binding")
trace_contract._emit_snapshots_state("p0", "instructional_injections", "state_snapshot")

trace_contract._emit_emits_metric_event("instructional_injections", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("instructional_injections", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("instructional_injections", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("instructional_injections", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("instructional_injections", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("instructional_injections", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("instructional_injections", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("instructional_injections", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("instructional_injections", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("instructional_injections", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("instructional_injections", "p4obs", "alert")
trace_contract._emit_links_incident_trace("instructional_injections", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("instructional_injections", "p3lm", "pattern")
trace_contract._emit_records_learning_event("instructional_injections", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("instructional_injections", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("instructional_injections", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("instructional_injections", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("instructional_injections", "p3lm", "policy")
trace_contract._emit_stores_learning_state("instructional_injections", "p3lm", "state")
trace_contract._emit_records_execution_trace("instructional_injections", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("instructional_injections", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("instructional_injections", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("instructional_injections", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("instructional_injections", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("instructional_injections", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("instructional_injections", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("instructional_injections", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("instructional_injections", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "instructional_injections", "context_pull")
trace_contract._emit_pulls_context("p1", "instructional_injections", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "instructional_injections", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "instructional_injections", "uwg_term_2")
trace_contract._emit_writes_through("p1", "instructional_injections", "write_through")
trace_contract._emit_writes_through("p1", "instructional_injections", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "instructional_injections", "safety_validation")
trace_contract._emit_invokes_eval("p1", "instructional_injections", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "instructional_injections", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "instructional_injections", "human_escalation")
trace_contract._emit_routes_through("p1", "instructional_injections", "route_through")
trace_contract._emit_checks_agent_registry("p1", "instructional_injections", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "instructional_injections", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "instructional_injections", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "instructional_injections", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "instructional_injections", "target_agent")
trace_contract._emit_verifies_policy("p1", "instructional_injections", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "instructional_injections", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "instructional_injections", "boundary_check")
trace_contract._emit_transcripts_response("p1", "instructional_injections", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "instructional_injections")
trace_contract._emit_gated_by_confidence("p1", "instructional_injections", "confidence_gate")
trace_contract.emit_replay_key("p0", "instructional_injections")
trace_contract.emit_determinism_digest("p0", "instructional_injections")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "instructional_injections", "execution_auth")
trace_contract._emit_validates_capability("p2", "instructional_injections", "capability_check")
trace_contract._emit_routes_to_capability("p2", "instructional_injections", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "instructional_injections", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "instructional_injections", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "instructional_injections", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "instructional_injections", "exec_output")
trace_contract._emit_dispatches_agent("p3", "instructional_injections", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "instructional_injections", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "instructional_injections", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "instructional_injections", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "instructional_injections", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "instructional_injections", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "instructional_injections", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "instructional_injections", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "instructional_injections", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "instructional_injections", "eval_metric")
trace_contract._emit_stores_embedding("p4", "instructional_injections", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "instructional_injections", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "instructional_injections", "exec_snapshot_link")

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
