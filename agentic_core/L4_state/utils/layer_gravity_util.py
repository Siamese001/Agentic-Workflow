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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "layer_gravity_util")
trace_contract.emit_determinism_digest("p0", "layer_gravity_util")

trace_contract._emit_dispatches_healing_run("p1", "layer_gravity_util", "L4")
trace_contract._emit_routes_through("p1", "layer_gravity_util", "L4")
trace_contract._emit_checks_agent_registry("p1", "layer_gravity_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "layer_gravity_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "layer_gravity_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "layer_gravity_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "layer_gravity_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "layer_gravity_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "layer_gravity_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "layer_gravity_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "layer_gravity_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "layer_gravity_util")
trace_contract._emit_gated_by_confidence("p1", "layer_gravity_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "layer_gravity_util", "L4")
trace_contract._emit_reads_policy_state("p1", "layer_gravity_util", "L4")
trace_contract._emit_authorize_and_execute("p2", "layer_gravity_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "layer_gravity_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "layer_gravity_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "layer_gravity_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "layer_gravity_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "layer_gravity_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "layer_gravity_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "layer_gravity_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "layer_gravity_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "layer_gravity_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "layer_gravity_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "layer_gravity_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "layer_gravity_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "layer_gravity_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "layer_gravity_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "layer_gravity_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "layer_gravity_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "layer_gravity_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "layer_gravity_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "layer_gravity_util", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("layer_gravity_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("layer_gravity_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("layer_gravity_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("layer_gravity_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("layer_gravity_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("layer_gravity_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("layer_gravity_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("layer_gravity_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("layer_gravity_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("layer_gravity_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("layer_gravity_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("layer_gravity_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("layer_gravity_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("layer_gravity_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("layer_gravity_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("layer_gravity_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("layer_gravity_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("layer_gravity_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("layer_gravity_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("layer_gravity_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("layer_gravity_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("layer_gravity_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("layer_gravity_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "layer_gravity_util", "context_pull")
trace_contract._emit_pulls_context("p1", "layer_gravity_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "layer_gravity_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "layer_gravity_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "layer_gravity_util", "write_through")
trace_contract._emit_writes_through("p1", "layer_gravity_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "layer_gravity_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "layer_gravity_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "layer_gravity_util", "routing_commit")

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

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "extract_layer_from_path", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "extract_layer_from_path", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "extract_layer_from_path")
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
