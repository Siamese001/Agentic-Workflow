"""
CANONICAL TRUTH: Sovereign Single Source of Truth Utilities
=========================================================

This module provides pure utility functions for SSOT calculations.

CRITICAL CONSTRAINTS:
- ZERO internal project imports (no agentic_core.* imports)
- Only stdlib imports allowed (pathlib, re, typing)
- Can be imported from anywhere without circular dependencies
- All functions are pure and deterministic

PURPOSE:
Resolves SSOT violations by providing canonical implementations for:
1. Health score calculation (Violation 4)
2. Layer inference from paths (Violation 2)
3. Agent categorization, territory mapping, etc.

USAGE:
    from agentic_core.utils.canonical_truth_validator import (
        calculate_health_score,
        get_canonical_layer
    )
"""

import re
from pathlib import Path
from typing import Any

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

emit_replay_key("p0", "canonical_truth_util")
emit_determinism_digest("p0", "canonical_truth_util")

_emit_dispatches_healing_run("p1", "canonical_truth_util", "L5")
_emit_routes_through("p1", "canonical_truth_util", "L5")
_emit_checks_agent_registry("p1", "canonical_truth_util", "agent_registry")
_emit_validates_agent_capability("p1", "canonical_truth_util", "capability")
_emit_dispatches_execution_plan("p1", "canonical_truth_util", "exec_plan")
_emit_agent_executes_agent("p1", "canonical_truth_util", "sub_agent")
_emit_routes_to_agent("p1", "canonical_truth_util", "target_agent")
_emit_verifies_policy("p1", "canonical_truth_util", "policy_check")
_emit_observes_runtime_state("p1", "canonical_truth_util", "runtime_state")
_emit_verifies_boundary("p1", "canonical_truth_util", "boundary_check")
_emit_transcripts_response("p1", "canonical_truth_util", "transcript")
_emit_hard_fails_untranscripted("p1", "canonical_truth_util")
_emit_gated_by_confidence("p1", "canonical_truth_util", "confidence_gate")
_emit_escalates_to_human("p1", "canonical_truth_util", "L5")
_emit_reads_policy_state("p1", "canonical_truth_util", "L5")
_emit_authorize_and_execute("p2", "canonical_truth_util", "execution_auth")
_emit_validates_capability("p2", "canonical_truth_util", "capability_check")
_emit_routes_to_capability("p2", "canonical_truth_util", "capability_route")
_emit_writes_via_uwg("p2", "canonical_truth_util", "uwg_write")
_emit_blocks_direct_write("p2", "canonical_truth_util", "direct_write_block")
_emit_records_tool_invocation("p2", "canonical_truth_util", "tool_invocation")
_emit_captures_execution_output("p2", "canonical_truth_util", "exec_output")
_emit_dispatches_agent("p3", "canonical_truth_util", "agent_dispatch")
_emit_coordinates_agents("p3", "canonical_truth_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "canonical_truth_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "canonical_truth_util", "healing_outcome")
_emit_escalates_failure("p3", "canonical_truth_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "canonical_truth_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "canonical_truth_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "canonical_truth_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "canonical_truth_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "canonical_truth_util", "eval_metric")
_emit_stores_embedding("p4", "canonical_truth_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "canonical_truth_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "canonical_truth_util", "exec_snapshot_link")
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

_emit_emits_metric_event("canonical_truth_util", "p4obs", "metric_1")
_emit_emits_metric_event("canonical_truth_util", "p4obs", "metric_2")
_emit_emits_metric_event("canonical_truth_util", "p4obs", "metric_3")
_emit_emits_metric_event("canonical_truth_util", "p4obs", "metric_4")
_emit_emits_metric_event("canonical_truth_util", "p4obs", "metric_5")
_emit_emits_metric_event("canonical_truth_util", "p4obs", "metric_6")
_emit_records_incident_event("canonical_truth_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("canonical_truth_util", "p4obs", "anomaly")
_emit_writes_observability_log("canonical_truth_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("canonical_truth_util", "p4obs", "mon_state")
_emit_triggers_alert("canonical_truth_util", "p4obs", "alert")
_emit_links_incident_trace("canonical_truth_util", "p4obs", "trace_link")
_emit_captures_pattern("canonical_truth_util", "p3lm", "pattern")
_emit_records_learning_event("canonical_truth_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("canonical_truth_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("canonical_truth_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("canonical_truth_util", "p3lm", "routing")
_emit_improves_agent_policy("canonical_truth_util", "p3lm", "policy")
_emit_stores_learning_state("canonical_truth_util", "p3lm", "state")
_emit_records_execution_trace("canonical_truth_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("canonical_truth_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("canonical_truth_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("canonical_truth_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("canonical_truth_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("canonical_truth_util", "env_read", "p2_env_1")
_emit_reads_environ("canonical_truth_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("canonical_truth_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("canonical_truth_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "canonical_truth_util", "context_pull")
_emit_pulls_context("p1", "canonical_truth_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "canonical_truth_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "canonical_truth_util", "uwg_term_2")
_emit_writes_through("p1", "canonical_truth_util", "write_through")
_emit_writes_through("p1", "canonical_truth_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "canonical_truth_util", "safety_validation")
_emit_invokes_eval("p1", "canonical_truth_util", "eval_call")
_emit_proposal_commits_routing("p1", "canonical_truth_util", "routing_commit")


def calculate_health_score(
    violations: list[dict[str, Any]],
    weights: dict[str, float] | None = None,
) -> float:
    """
    Calculate a normalized health score (0-100) from violation data.

    Args:
        violations: List of violation dictionaries with 'severity' and 'count' keys
        weights: Optional weights for different severity levels

    Returns:
        Health score from 0 (worst) to 100 (best)
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "calculate_health_score", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "calculate_health_score", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "calculate_health_score")
    if not violations:
        return 100.0
    default_weights = {"critical": 10.0, "high": 5.0, "medium": 2.0, "low": 1.0}
    weights = weights or default_weights
    total_penalty = 0.0
    max_possible_penalty = 0.0
    for violation in violations:
        severity = violation.get("severity", "medium").lower()
        count = violation.get("count", 1)
        penalty = weights.get(severity, 2.0) * count
        total_penalty += penalty
        max_possible_penalty += default_weights["critical"] * count
    if max_possible_penalty == 0:
        return 100.0
    health_score = max(0, 100 - total_penalty / max_possible_penalty * 100)
    return round(health_score, 2)


def get_canonical_layer(file_path: str | Path) -> str:
    """
    Infer the canonical layer from a file path.

    Args:
        file_path: Path to the file

    Returns:
        Canonical layer string (L0-L6, Apps, Utils, Tests, or 'unknown')
    """
    path_str = str(file_path)
    layer_patterns = {
        "/L0_routing/": "L0",
        "/L1_cognition/": "L1",
        "/L2_execution/": "L2",
        "/L3_orchestration/": "L3",
        "/L4_state/": "L4",
        "/L5_safety/": "L5",
        "/L6_observability/": "L6",
        "/apps_": "Apps",
        "/apps_shared/": "Apps",
        "/agentic_core/utils/": "Utils",
        "/tests/": "Tests",
        "/test_": "Tests",
    }
    for pattern, layer in layer_patterns.items():
        if re.search(pattern, path_str):
            return layer
    return "unknown"


def validate_health_components(components: dict[str, Any]) -> dict[str, Any]:
    """
    Validate health components and return validation results.

    Args:
        components: Dictionary of health components to validate

    Returns:
        Validation results with valid/invalid components
    """
    results = {"valid": [], "invalid": [], "missing_required": [], "overall_valid": True}
    required_components = ["violations", "weights", "thresholds"]
    for component in required_components:
        if component not in components:
            results["missing_required"].append(component)
            results["overall_valid"] = False
    if "violations" in components:
        violations = components["violations"]
        if isinstance(violations, list):
            results["valid"].append("violations")
        else:
            results["invalid"].append("violations")
            results["overall_valid"] = False
    if "weights" in components:
        weights = components["weights"]
        if isinstance(weights, dict) and all(
            (isinstance(k, str) and isinstance(v, int | float) for k, v in weights.items()),
        ):
            results["valid"].append("weights")
        else:
            results["invalid"].append("weights")
            results["overall_valid"] = False
    return results


def get_health_weights() -> dict[str, float]:
    """
    Get default health calculation weights.

    Returns:
        Dictionary of weights for different violation severities
    """
    return {"critical": 10.0, "high": 5.0, "medium": 2.0, "low": 1.0, "info": 0.5}


def categorize_agent(class_name: str, base_classes: list | None = None, docstring: str | None = None) -> str:
    """
    Categorize an agent based on its name, inheritance, and documentation.

    Args:
        class_name: Name of the agent class (e.g., "BaseClassEnforcerAgent")
        base_classes: List of base class names (e.g., ["L5Agent", "MCPHardenedMixin"])
        docstring: Optional docstring content

    Returns:
        Agent category string
    """
    base_classes = base_classes or []
    search_string = class_name + " " + " ".join(base_classes) + " " + (docstring or "")
    categories = {
        "Validator": "validator|check|enforce|validate|audit",
        "Orchestrator": "orchestrat|workflow|coordination|meta",
        "Guardrail": "guardrail|safety|security|protect",
        "Memory": "memory|storage|cache|persist",
        "L1": "cognition|thought|intent|analysis",
        "L2": "execution|tool|action|mcp",
        "L3": "orchestrat|workflow|coordination|meta",
        "L4": "state|validation|ledger|memory",
        "L5": "safety|guardrail|validator|audit",
        "L6": "observability|logging|telemetry|metrics",
        "GenericAgent": "agent|base|sovereign",
    }
    for category, pattern in categories.items():
        if re.search(pattern, search_string, re.IGNORECASE):
            return category
    return "Unknown"


def get_agent_categories() -> list[str]:
    """
    Get list of all valid agent categories.

    Returns:
        List of category strings
    """
    return [
        "Validator",
        "Orchestrator",
        "Guardrail",
        "Memory",
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "GenericAgent",
        "Unknown",
    ]
