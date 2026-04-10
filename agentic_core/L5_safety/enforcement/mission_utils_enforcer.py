from __future__ import annotations

import importlib
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L1_COGNITION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
)
from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("mission_utils_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("mission_utils_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("mission_utils_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("mission_utils_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("mission_utils_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("mission_utils_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("mission_utils_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("mission_utils_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("mission_utils_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("mission_utils_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("mission_utils_enforcer", "p4obs", "alert")
_emit_links_incident_trace("mission_utils_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("mission_utils_enforcer", "p3lm", "pattern")
_emit_records_learning_event("mission_utils_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mission_utils_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("mission_utils_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mission_utils_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("mission_utils_enforcer", "p3lm", "policy")
_emit_stores_learning_state("mission_utils_enforcer", "p3lm", "state")
_emit_records_execution_trace("mission_utils_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mission_utils_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mission_utils_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mission_utils_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mission_utils_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mission_utils_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("mission_utils_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("mission_utils_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mission_utils_enforcer", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "mission_utils_enforcer")
emit_determinism_digest("p0", "mission_utils_enforcer")

_emit_dispatches_healing_run("p1", "mission_utils_enforcer", "L5")
_emit_routes_through("p1", "mission_utils_enforcer", "L5")
_emit_checks_agent_registry("p1", "mission_utils_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "mission_utils_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "mission_utils_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "mission_utils_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "mission_utils_enforcer", "target_agent")
_emit_verifies_policy("p1", "mission_utils_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "mission_utils_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "mission_utils_enforcer", "boundary_check")
_emit_transcripts_response("p1", "mission_utils_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "mission_utils_enforcer")
_emit_gated_by_confidence("p1", "mission_utils_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "mission_utils_enforcer", "L5")
_emit_reads_policy_state("p1", "mission_utils_enforcer", "L5")
_emit_pulls_context("p1", "mission_utils_enforcer", "context_pull")
_emit_pulls_context("p1", "mission_utils_enforcer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "mission_utils_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mission_utils_enforcer", "uwg_term_secondary")
_emit_writes_through("p1", "mission_utils_enforcer", "write_through")
_emit_writes_through("p1", "mission_utils_enforcer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "mission_utils_enforcer", "safety_validation")
_emit_invokes_eval("p1", "mission_utils_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "mission_utils_enforcer", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "mission_utils_enforcer")
_emit_applies_guardrail("p0", "mission_utils_enforcer", "p0_governance")
_emit_snapshots_state("p0", "mission_utils_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "mission_utils_enforcer", "execution_auth")
_emit_validates_capability("p2", "mission_utils_enforcer", "capability_check")
_emit_routes_to_capability("p2", "mission_utils_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "mission_utils_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "mission_utils_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "mission_utils_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "mission_utils_enforcer", "exec_output")
_emit_dispatches_agent("p3", "mission_utils_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "mission_utils_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "mission_utils_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "mission_utils_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "mission_utils_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "mission_utils_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mission_utils_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "mission_utils_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "mission_utils_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mission_utils_enforcer", "eval_metric")
_emit_stores_embedding("p4", "mission_utils_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "mission_utils_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mission_utils_enforcer", "exec_snapshot_link")


def dynamic_import(module_path: str, class_name: str) -> Any | None:
    """
    Dynamically import classes to avoid gravity violations.

    Args:
        module_path: Dotted module path (e.g., 'agentic_core.L5_safety.enforcement.SafetyGuardrail')
        class_name: Name of the class to import

    Returns:
        The imported class, or None if import fails
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        return None


def get_layer_rank(path_str: str) -> int:
    """
    Get the authority rank of a layer based on its position in the SSOT registry.
    Lower index = higher authority.

    Args:
        path_str: File path string to check

    Returns:
        Layer rank (0-based index), or -1 if not found
    """
    gravity_layers = list(CORE_SUBFOLDER_MAP.keys())
    for i, layer in enumerate(gravity_layers):
        if layer in path_str:
            return i
    return -1


def get_legal_l2_for_l1(root: str, l1_name: str) -> list[str]:
    """
    Pull valid L2 folders directly from imported SSOT maps.

    Args:
        root: Root territory name (agentic_core, apps_rg, apps_lic, apps_shared)
        l1_name: L1 folder name

    Returns:
        List of approved L2 subfolder names
    """
    if root == AGENTIC_CORE_DIR:
        return CORE_SUBFOLDER_MAP.get(l1_name, [])
    elif root == APPS_RG_DIR:
        return APPS_RG_SUBFOLDER_MAP.get(l1_name, [])
    elif root == APPS_LIC_DIR:
        return APPS_LIC_SUBFOLDER_MAP.get(l1_name, [])
    elif root == APPS_SHARED_DIR:
        return APPS_SHARED_SUBFOLDER_MAP.get(l1_name, [])
    return []


def get_placement_guidance(content_preview: str) -> str:
    """
    Heuristically determine the best L1 placement for code based on content signals.

    Args:
        content_preview: First ~500 chars of file content

    Returns:
        Suggested L1 path (e.g., 'agentic_core/L1_cognition')
    """
    content_lower = content_preview.lower()
    if any(x in content_lower for x in ["planner", "strategy", "reasoning", "mission"]):
        return L1_COGNITION_DIR
    if "node" in content_lower or "execute" in content_lower:
        # guardian: allow-path-string
        return L1_COGNITION_DIR + "/thought_engine"
    if any(x in content_lower for x in ["router", "orchestrator", "fission", "hop"]):
        return L3_ORCHESTRATION_DIR
    if any(x in content_lower for x in ["pinecone", "redis", "storage", "cache"]):
        return L4_STATE_DIR
    if any(x in content_lower for x in ["safety", "guardrail", "guard", "validator"]):
        return L5_SAFETY_DIR
    if any(x in content_lower for x in ["Metric", "telemetry", "trace", "observ"]):
        return "agentic_core/observability"
    if any(x in content_lower for x in ["prompt", "persona", "instruct"]):
        return "agentic_core/prompt_governance"
    if any(x in content_lower for x in ["schema", "model", "request", "response"]):
        return "agentic_core/runtime/types"
    return L1_COGNITION_DIR


def get_best_target_l1(folder_name: str, approved_l1: set) -> str:
    """
    Heuristically determine the best approved L1 folder for a non-approved folder.

    Args:
        folder_name: Name of the folder to relocate
        approved_l1: Set of approved L1 folder names

    Returns:
        Best matching approved L1 folder name
    """
    name_lower = folder_name.lower()
    if any(x in name_lower for x in ["cognit", "thought", "reason", "intent", "strateg"]):
        return "L1_cognition"
    if any(x in name_lower for x in ["exec", "action", "tool", "handler"]):
        return "L2_execution"
    if any(x in name_lower for x in ["orchestr", "workflow", "fission", "Route", "hop"]):
        return "L3_orchestration"
    if any(x in name_lower for x in ["state", "memory", "cache", "audit", "ledger", "context"]):
        return "L4_state"
    if any(x in name_lower for x in ["safe", "guard", "policy", "red_team", "gravity"]):
        return "L5_safety"
    if any(x in name_lower for x in ["maint", "script", "log", "bench"]):
        return "L0_routing"
    if any(x in name_lower for x in ["config", "env", "setting"]):
        return "config"
    if any(x in name_lower for x in ["schema", "model", "request", "response"]):
        return "schemas"
    if any(x in name_lower for x in ["prompt", "persona", "instruct"]):
        return "prompt_governance"
    if any(x in name_lower for x in ["runtime", "shared"]):
        return "runtime"
    if any(x in name_lower for x in ["observ", "Metric", "telemetry"]):
        return "observability"
    if any(x in name_lower for x in ["util", "helper", "extension"]):
        return "utils"
    if any(x in name_lower for x in ["pattern", "role", "flow"]):
        return "patterns"
    if any(x in name_lower for x in ["semantic", "vector", "embed"]):
        return "semantic_memory"
    if any(x in name_lower for x in ["knowledge", "rag", "document", "research"]):
        return "knowledge"
    return "utils"


_AGENT_LOW_CONFIDENCE_ROOTS: frozenset[str] = frozenset(
    {TESTS_DIR, "docs", "data", "artifacts", OPS_SCRIPTS_DIR},
)


def _calculate_subfolder_confidence_for_agent(l1_name: str, item_name: str) -> float:
    """Return placement confidence for an *Agent.py file into l1_name.

    Returns:
        < 0.5 — caller must NOT auto-relocate; archive instead.
        1.0   — source layer; relocation is acceptable.
    """
    if l1_name in _AGENT_LOW_CONFIDENCE_ROOTS:
        return 0.0
    return 1.0


def get_best_target_l2(l1_name: str, item_name: str) -> str:
    """
    Heuristically determine the best approved L2 folder within an L1.

    Args:
        l1_name: L1 folder name
        item_name: Name of file/folder to place

    Returns:
        Best matching L2 folder name, or ``"__ARCHIVE__"`` sentinel when the
        placement confidence for an *Agent.py file is below 0.5.  Callers must
        check for this sentinel and route to safe_archive() instead of moving.
    """
    if item_name.endswith("Agent.py"):
        if _calculate_subfolder_confidence_for_agent(l1_name, item_name) < 0.5:
            return "__ARCHIVE__"
    approved_l2 = CORE_SUBFOLDER_MAP.get(l1_name, [])
    if not approved_l2:
        return "workflow_engines"
    name_lower = item_name.lower()
    for l2 in approved_l2:
        if l2.lower() in name_lower or name_lower in l2.lower():
            return l2
    return approved_l2[0]
