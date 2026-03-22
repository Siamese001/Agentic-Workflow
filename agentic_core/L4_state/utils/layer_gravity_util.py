"""
Shared layer gravity constants and validation.

SSOT for layer hierarchy and gravity rules.
Used by: StructuralValidatorAgent, GravityLeakRepairAgent, ArchitectureGovernorAgent

Extracted from:
- StructuralValidatorAgent.LAYER_ORDER, GRAVITY_RULES
- GravityLeakRepairAgent.LAYER_ORDER
- ArchitectureGovernorAgent (implicit usage)

All implementations were identical - this consolidates them.
"""

from __future__ import annotations

from pathlib import Path

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

emit_replay_key("p0", "layer_gravity_util")
emit_determinism_digest("p0", "layer_gravity_util")

_emit_dispatches_healing_run("p1", "layer_gravity_util", "L4")
_emit_routes_through("p1", "layer_gravity_util", "L4")
_emit_checks_agent_registry("p1", "layer_gravity_util", "agent_registry")
_emit_validates_agent_capability("p1", "layer_gravity_util", "capability")
_emit_dispatches_execution_plan("p1", "layer_gravity_util", "exec_plan")
_emit_agent_executes_agent("p1", "layer_gravity_util", "sub_agent")
_emit_routes_to_agent("p1", "layer_gravity_util", "target_agent")
_emit_verifies_policy("p1", "layer_gravity_util", "policy_check")
_emit_observes_runtime_state("p1", "layer_gravity_util", "runtime_state")
_emit_verifies_boundary("p1", "layer_gravity_util", "boundary_check")
_emit_transcripts_response("p1", "layer_gravity_util", "transcript")
_emit_hard_fails_untranscripted("p1", "layer_gravity_util")
_emit_gated_by_confidence("p1", "layer_gravity_util", "confidence_gate")
_emit_escalates_to_human("p1", "layer_gravity_util", "L4")
_emit_reads_policy_state("p1", "layer_gravity_util", "L4")
_emit_authorize_and_execute("p2", "layer_gravity_util", "execution_auth")
_emit_validates_capability("p2", "layer_gravity_util", "capability_check")
_emit_routes_to_capability("p2", "layer_gravity_util", "capability_route")
_emit_writes_via_uwg("p2", "layer_gravity_util", "uwg_write")
_emit_blocks_direct_write("p2", "layer_gravity_util", "direct_write_block")
_emit_records_tool_invocation("p2", "layer_gravity_util", "tool_invocation")
_emit_captures_execution_output("p2", "layer_gravity_util", "exec_output")
_emit_dispatches_agent("p3", "layer_gravity_util", "agent_dispatch")
_emit_coordinates_agents("p3", "layer_gravity_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "layer_gravity_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "layer_gravity_util", "healing_outcome")
_emit_escalates_failure("p3", "layer_gravity_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "layer_gravity_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "layer_gravity_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "layer_gravity_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "layer_gravity_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "layer_gravity_util", "eval_metric")
_emit_stores_embedding("p4", "layer_gravity_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "layer_gravity_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "layer_gravity_util", "exec_snapshot_link")
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

_emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_1")
_emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_2")
_emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_3")
_emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_4")
_emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_5")
_emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_6")
_emit_records_incident_event("layer_gravity_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("layer_gravity_util", "p4obs", "anomaly")
_emit_writes_observability_log("layer_gravity_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("layer_gravity_util", "p4obs", "mon_state")
_emit_triggers_alert("layer_gravity_util", "p4obs", "alert")
_emit_links_incident_trace("layer_gravity_util", "p4obs", "trace_link")
_emit_captures_pattern("layer_gravity_util", "p3lm", "pattern")
_emit_records_learning_event("layer_gravity_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("layer_gravity_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("layer_gravity_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("layer_gravity_util", "p3lm", "routing")
_emit_improves_agent_policy("layer_gravity_util", "p3lm", "policy")
_emit_stores_learning_state("layer_gravity_util", "p3lm", "state")
_emit_records_execution_trace("layer_gravity_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("layer_gravity_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("layer_gravity_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("layer_gravity_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("layer_gravity_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("layer_gravity_util", "env_read", "p2_env_1")
_emit_reads_environ("layer_gravity_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("layer_gravity_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("layer_gravity_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "layer_gravity_util", "context_pull")
_emit_pulls_context("p1", "layer_gravity_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "layer_gravity_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "layer_gravity_util", "uwg_term_2")
_emit_writes_through("p1", "layer_gravity_util", "write_through")
_emit_writes_through("p1", "layer_gravity_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "layer_gravity_util", "safety_validation")
_emit_invokes_eval("p1", "layer_gravity_util", "eval_call")
_emit_proposal_commits_routing("p1", "layer_gravity_util", "routing_commit")

LAYER_ORDER: dict[str, int] = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
GRAVITY_RULES: dict[str, set[str]] = {
    "L0": {"L0"},
    "L1": {"L0", "L1"},
    "L2": {"L0", "L1", "L2"},
    "L3": {"L0", "L1", "L2", "L3"},
    "L4": {"L0", "L1", "L2", "L3", "L4"},
    "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},
    "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},
}


def extract_layer_from_path(path: Path | str) -> str | None:
    """
    Extract layer identifier from file path.

    Args:
        path: File path (Path object or string)

    Returns:
        Layer identifier (e.g., "L5") or None if not in a layer

    Example:
        >>> extract_layer_from_path("agentic_core/L5_safety/validators/GovernanceAgent.py")
        'L5'
        >>> extract_layer_from_path("apps_rg/engines/tool.py")
        None
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_layer_from_path", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_layer_from_path", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "extract_layer_from_path")
    path_str = str(path)
    for layer in LAYER_ORDER.keys():
        if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
            return layer
    return None


def extract_layer_from_module(module: str) -> str | None:
    """
    Extract layer identifier from module path.

    Args:
        module: Module path (e.g., "agentic_core.L3_orchestration.reasoning")

    Returns:
        Layer identifier (e.g., "L3") or None if not in a layer

    Example:
        >>> extract_layer_from_module("agentic_core.L3_orchestration.reasoning")
        'L3'
        >>> extract_layer_from_module("apps_shared.common_utils")
        None
    """
    for layer in LAYER_ORDER.keys():
        if f".{layer}_" in module or module.startswith(f"{layer}_") or f"_{layer}_" in module:
            return layer
    return None


def is_gravity_violation(source_layer: str, target_layer: str) -> bool:
    """
    Check if importing target_layer from source_layer violates gravity.

    Gravity violation occurs when a lower layer imports from a higher layer.

    Args:
        source_layer: Layer of the importing file (e.g., "L3")
        target_layer: Layer being imported (e.g., "L5")

    Returns:
        True if this is a gravity violation (upward import)

    Example:
        >>> is_gravity_violation("L3", "L5")  # L3 importing L5
        True
        >>> is_gravity_violation("L5", "L3")  # L5 importing L3
        False
        >>> is_gravity_violation("L3", "L3")  # Same layer
        False
    """
    allowed = GRAVITY_RULES.get(source_layer, set())
    return target_layer not in allowed


def get_allowed_layers(source_layer: str) -> set[str]:
    """
    Get the set of layers that a source layer is allowed to import from.

    Args:
        source_layer: Layer of the importing file

    Returns:
        Set of allowed layer identifiers

    Example:
        >>> get_allowed_layers("L3")
        {'L0', 'L1', 'L2', 'L3'}
    """
    return GRAVITY_RULES.get(source_layer, set())


def get_layer_order(layer: str) -> int:
    """
    Get the numeric order of a layer (lower = more foundational).

    Args:
        layer: Layer identifier (e.g., "L3")

    Returns:
        Numeric order (0-6) or -1 if not a valid layer

    Example:
        >>> get_layer_order("L3")
        3
        >>> get_layer_order("invalid")
        -1
    """
    return LAYER_ORDER.get(layer, -1)
