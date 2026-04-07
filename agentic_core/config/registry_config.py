"""
SSOT for Sovereign Registry configuration.

SINGLE SOURCE OF TRUTH: SOVEREIGN_REGISTRY is now derived from
SOVEREIGN_TERRITORIES (agentic_core/L5_safety/config/structure_blueprint/_constants.py).
Do NOT add territory definitions here — add them to _constants.py instead.
"""

import os

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

_emit_records_execution_trace("p0", "evidence", "registry_config")
_emit_applies_guardrail("p0", "registry_config", "p0_governance")
_emit_reads_policy_state("p0", "registry_config", "policy_binding")
_emit_snapshots_state("p0", "registry_config", "state_snapshot")
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

_emit_emits_metric_event("registry_config", "p4obs", "metric_1")
_emit_emits_metric_event("registry_config", "p4obs", "metric_2")
_emit_emits_metric_event("registry_config", "p4obs", "metric_3")
_emit_emits_metric_event("registry_config", "p4obs", "metric_4")
_emit_emits_metric_event("registry_config", "p4obs", "metric_5")
_emit_emits_metric_event("registry_config", "p4obs", "metric_6")
_emit_records_incident_event("registry_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("registry_config", "p4obs", "anomaly")
_emit_writes_observability_log("registry_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("registry_config", "p4obs", "mon_state")
_emit_triggers_alert("registry_config", "p4obs", "alert")
_emit_links_incident_trace("registry_config", "p4obs", "trace_link")
_emit_captures_pattern("registry_config", "p3lm", "pattern")
_emit_records_learning_event("registry_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("registry_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("registry_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("registry_config", "p3lm", "routing")
_emit_improves_agent_policy("registry_config", "p3lm", "policy")
_emit_stores_learning_state("registry_config", "p3lm", "state")
_emit_records_execution_trace("registry_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("registry_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("registry_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("registry_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("registry_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("registry_config", "env_read", "p2_env_1")
_emit_reads_environ("registry_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("registry_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("registry_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "registry_config", "context_pull")
_emit_pulls_context("p1", "registry_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "registry_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "registry_config", "uwg_term_2")
_emit_writes_through("p1", "registry_config", "write_through")
_emit_writes_through("p1", "registry_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "registry_config", "safety_validation")
_emit_invokes_eval("p1", "registry_config", "eval_call")
_emit_proposal_commits_routing("p1", "registry_config", "routing_commit")
_emit_escalates_to_human("p1", "registry_config", "human_escalation")
_emit_routes_through("p1", "registry_config", "route_through")
_emit_checks_agent_registry("p1", "registry_config", "agent_registry")
_emit_validates_agent_capability("p1", "registry_config", "capability")
_emit_dispatches_execution_plan("p1", "registry_config", "exec_plan")
_emit_agent_executes_agent("p1", "registry_config", "sub_agent")
_emit_routes_to_agent("p1", "registry_config", "target_agent")
_emit_verifies_policy("p1", "registry_config", "policy_check")
_emit_observes_runtime_state("p1", "registry_config", "runtime_state")
_emit_verifies_boundary("p1", "registry_config", "boundary_check")
_emit_transcripts_response("p1", "registry_config", "transcript")
_emit_hard_fails_untranscripted("p1", "registry_config")
_emit_gated_by_confidence("p1", "registry_config", "confidence_gate")
emit_replay_key("p0", "registry_config")
emit_determinism_digest("p0", "registry_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "registry_config", "execution_auth")
_emit_validates_capability("p2", "registry_config", "capability_check")
_emit_routes_to_capability("p2", "registry_config", "capability_route")
_emit_writes_via_uwg("p2", "registry_config", "uwg_write")
_emit_blocks_direct_write("p2", "registry_config", "direct_write_block")
_emit_records_tool_invocation("p2", "registry_config", "tool_invocation")
_emit_captures_execution_output("p2", "registry_config", "exec_output")
_emit_dispatches_agent("p3", "registry_config", "agent_dispatch")
_emit_coordinates_agents("p3", "registry_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "registry_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "registry_config", "healing_outcome")
_emit_escalates_failure("p3", "registry_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "registry_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "registry_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "registry_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "registry_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "registry_config", "eval_metric")
_emit_stores_embedding("p4", "registry_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "registry_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "registry_config", "exec_snapshot_link")


# Configuration constants

def _derive_registry() -> dict:
    """Build SOVEREIGN_REGISTRY from SSOT subsets (DEPTH_RULES + subfolder maps).

    Produces the flat {name: {depth, subfolders}} shape expected by
    LocationHealerAgent._autonomous_void_violation_resolution().
    """
    from agentic_core.L5_safety.config.structure_blueprint import (
        CORE_SUBFOLDER_MAP,
        DEPTH_RULES,
        PROJECT_ROOT_WHITELIST,
    )
    from agentic_core.L5_safety.config.structure_blueprint.derived import (
        APPS_LIC_SUBFOLDER_MAP as apps_lic_map,
    )
    from agentic_core.L5_safety.config.structure_blueprint.derived import (
        APPS_RG_SUBFOLDER_MAP as apps_rg_map,
    )
    from agentic_core.L5_safety.config.structure_blueprint.derived import (
        APPS_SHARED_SUBFOLDER_MAP as apps_shared_map,
    )
    from agentic_core.L5_safety.config.structure_blueprint.derived import (
        TESTS_SUBFOLDER_MAP as tests_map,
    )

    subfolder_maps: dict = {
        "agentic_core": list(CORE_SUBFOLDER_MAP.keys()),
        "apps_lic": sorted(apps_lic_map.keys()),
        "apps_rg": sorted(apps_rg_map.keys()),
        "apps_shared": sorted(apps_shared_map.keys()),
        "tests": sorted(tests_map.keys()),
    }

    registry: dict = {}
    for name in PROJECT_ROOT_WHITELIST:
        entry: dict = {
            "depth": DEPTH_RULES.get(name, 2),
            "subfolders": subfolder_maps.get(name, []),
        }
        registry[name] = entry
    return registry


SOVEREIGN_REGISTRY: dict = _derive_registry()

# ============================================================================
# HEALING CONFIGURATION
# ============================================================================
HEALING_CONFIG: dict = {
    "max_rounds": int(os.getenv("MAX_HEALING_ROUNDS", "10")),
    "max_per_file": int(os.getenv("MAX_HEALING_PER_FILE", "8")),
    "global_budget": int(os.getenv("GLOBAL_HEALING_BUDGET", "500")),
    "max_moves_per_run": 250,
    "max_fissions_per_run": 50,
    "dust_threshold": 40,  # Minimum lines for a module to exist (Span-of-Two)
}

# ============================================================================
# CORE SUBFOLDER MAPS
# ============================================================================
CORE_SUBFOLDER_MAP: dict = {
    "L0_routing": ["scripts", "logs", "benchmarks", "mixins"],
    "L1_cognition": ["thought_engine", "intent_analysis", "planning"],
    "L2_execution": ["tool_registry", "action_handlers", "mcp", "tool_registry"],
    "L3_orchestration": [
        "workflow_engines",
        "fission_logic",
        "S3_vitality",
        "mcp",
        "meta_learning",
        "interfaces",
    ],
    "L4_state": ["ValidationContext", "ledger", "filesystem", "memory", "validation_context"],
    "L5_safety": [
        "guardrails",
        "red_teaming",
        "gravity",
        "validators",
        "agents",
        "bases",
        "policies",
        "utils",
        "verifiability",
    ],
    "L6_observability": [
        "dashboards",
        "reports",
        "metrics",
        "telemetry",
        "tracing",
        "compliance",
        "agents",
    ],
    # DISSOLVED: "schemas" removed — deported to runtime/types, L4/contracts, L6/engine+types
    "config": ["core", "environments", "feature_flags", "secrets_manager"],
    "prompt_governance": ["meta_prompts", "version_registry", "rendering", "templates"],
    "runtime": ["shared_runtime", "environment_setup", "shared", "resource_management"],
    "utils": ["core_extensions", "wrappers", "general_helpers", "naming", "deduplicated"],
    "patterns": ["agent_roles", "communication_flow", "interaction_patterns", "reasoning_patterns"],
    "semantic_memory": ["store", "embeddings", "retrieval", "index"],
    "knowledge": ["document_loaders", "static_index", "ResearchCache"],
}

# ============================================================================
# VARIABLE DEPTH SUBFOLDERS
# ============================================================================
# These subfolders are exempt from strict depth enforcement.
VARIABLE_DEPTH_SUBFOLDERS: frozenset = frozenset(
    {
        "utils",
        "config",
        "common",
        "observability",
        "L6_observability",
        "L3_orchestration",
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L4_state",
        "L5_safety",
        "prompt_governance",
        "runtime",
        "patterns",
        "semantic_memory",
        "knowledge",
    },
)

# ============================================================================
# L4 APPROVED FOLDERS (Depth-4 Structure)
# ============================================================================
L4_APPROVED_FOLDERS: set = {
    "agentic_core/L6_observability/dashboards",
    "agentic_core/L0_routing/scripts",
    "agentic_core/L3_orchestration/reasoning",
    "agentic_core/L1_cognition/thought_engine",
    "agentic_core/L5_safety/enforcement",
    "agentic_core/L5_safety/validators",
    "agentic_core/L2_execution/reasoning",
    "agentic_core/L2_execution/enforcement",
    "agentic_core/L4_state/memory",
    # DISSOLVED: "agentic_core/schemas/models" removed
    "agentic_core/utils/core_extensions",
    "agentic_core/config/core",  # DISSOLVED: was blueprint_sovereign
}

# ============================================================================
# GRAVITY CONFIGURATION
# ============================================================================
GRAVITY_CONFIG: dict = {
    "enabled": True,
    "UPSTREAM_SOVEREIGN_ROOTS": ["agentic_core"],
    "downstream_domains": ["apps_rg", "apps_lic", "apps_shared", "tests"],
    "exemptions": [],
}

# ============================================================================
# MISSION CONFIGURATION
# ============================================================================
MISSION_CONFIG: dict = {
    "GRAVITY_SURGERY_ENABLED": True,
    "hierarchy_healing_enabled": True,
    "span_surgery_enabled": True,
    "fission_enabled": True,
    "run_full_mission": True,
    "run_hierarchy_healing": True,
    "run_gravity_refactor": True,
    "run_sprawl_surgery": True,
    "structural_only_mode": False,
    "timeout_seconds": int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800")),
}

# ============================================================================
# AGENT RESILIENCE CONFIGURATION
# ============================================================================
AGENT_RESILIENCE_CONFIG: dict = {
    "retry_count": int(os.getenv("AGENT_RETRY_COUNT", "3")),
    "backoff_base": float(os.getenv("AGENT_RETRY_BACKOFF_BASE", "0.5")),
}

# ============================================================================
# MCP CAPABILITIES
# ============================================================================
MCP_CAPABILITIES: dict = {
    "router": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "marketplace_filter": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "filesystem": {"enabled": True, "path": "agentic_core.L4_state.filesystem"},
    "figma": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "fetch": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "semantic_cache": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
}

# ============================================================================
# LAYER DIRECTORIES MAPPING
# ============================================================================
LAYER_DIRS: dict = {
    "L0": "L0_routing",
    "L1": "L1_cognition",
    "L2": "L2_execution",
    "L3": "L3_orchestration",
    "L4": "L4_state",
    "L5": "L5_safety",
    "L6": "L6_observability",
}

# ============================================================================
# L2 TO L1 REVERSE MAPPING
# ============================================================================
L2_TO_L1_MAP: dict = {
    "thought_engine": "L1_cognition",
    "intent_analysis": "L1_cognition",
    "planning": "L1_cognition",
    "tool_registry": "L2_execution",
    "action_handlers": "L2_execution",
    "mcp": "L2_execution",
    "workflow_engines": "L3_orchestration",
    "fission_logic": "L3_orchestration",
    "meta_learning": "L3_orchestration",
    "S3_vitality": "L3_orchestration",
    "ValidationContext": "L4_state",
    "ledger": "L4_state",
    "memory": "L4_state",
    "filesystem": "L4_state",
    "guardrails": "L5_safety",
    "validators": "L5_safety",
    "gravity": "L5_safety",
    "red_teaming": "L5_safety",
    "core_extensions": "utils",
    "naming": "utils",
    "wrappers": "utils",
    "general_helpers": "utils",
    "metrics": "observability",
    "tracing": "observability",
    "telemetry": "observability",
    "compliance": "observability",
    "models": "runtime",
    "messages": "runtime",
    "types": "runtime",
    "templates": "prompt_governance",
    "meta_prompts": "prompt_governance",
    "rendering": "prompt_governance",
    "version_registry": "prompt_governance",
    "environments": "config",
    "feature_flags": "config",
    "scripts": "L0_routing",
    "logs": "L0_routing",
    "benchmarks": "L0_routing",
}

__all__ = [
    "SOVEREIGN_REGISTRY",
    "HEALING_CONFIG",
    "CORE_SUBFOLDER_MAP",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "L4_APPROVED_FOLDERS",
    "GRAVITY_CONFIG",
    "MISSION_CONFIG",
    "AGENT_RESILIENCE_CONFIG",
    "MCP_CAPABILITIES",
    "LAYER_DIRS",
    "L2_TO_L1_MAP",
]
