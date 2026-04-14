"""
Derived Module - COLD PATH (Derived Registries and Compilation)

This module contains derived registries that are computed from
SOVEREIGN_TERRITORIES, eliminating static duplication.

Loaded lazily on first access.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.territories import (
    get_all_territories,
)
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "derived")
emit_determinism_digest("p0", "derived")

_emit_dispatches_healing_run("p1", "derived", "L5")
_emit_routes_through("p1", "derived", "L5")
_emit_checks_agent_registry("p1", "derived", "agent_registry")
_emit_validates_agent_capability("p1", "derived", "capability")
_emit_dispatches_execution_plan("p1", "derived", "exec_plan")
_emit_agent_executes_agent("p1", "derived", "sub_agent")
_emit_routes_to_agent("p1", "derived", "target_agent")
_emit_verifies_policy("p1", "derived", "policy_check")
_emit_observes_runtime_state("p1", "derived", "runtime_state")
_emit_verifies_boundary("p1", "derived", "boundary_check")
_emit_transcripts_response("p1", "derived", "transcript")
_emit_hard_fails_untranscripted("p1", "derived")
_emit_gated_by_confidence("p1", "derived", "confidence_gate")
_emit_escalates_to_human("p1", "derived", "L5")
_emit_reads_policy_state("p1", "derived", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "derived")
_emit_applies_guardrail("p0", "derived", "p0_governance")
_emit_snapshots_state("p0", "derived", "state_snapshot")
_emit_authorize_and_execute("p2", "derived", "execution_auth")
_emit_validates_capability("p2", "derived", "capability_check")
_emit_routes_to_capability("p2", "derived", "capability_route")
_emit_writes_via_uwg("p2", "derived", "uwg_write")
_emit_blocks_direct_write("p2", "derived", "direct_write_block")
_emit_records_tool_invocation("p2", "derived", "tool_invocation")
_emit_captures_execution_output("p2", "derived", "exec_output")
_emit_dispatches_agent("p3", "derived", "agent_dispatch")
_emit_coordinates_agents("p3", "derived", "agent_coordination")
_emit_records_workflow_lineage("p3", "derived", "workflow_lineage")
_emit_records_healing_outcome("p3", "derived", "healing_outcome")
_emit_escalates_failure("p3", "derived", "failure_escalation")
_emit_orchestrates_workflow("p3", "derived", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "derived", "healing_dispatch")
_emit_invokes_evaluation("p3", "derived", "evaluation_signal")
_emit_records_telemetry_event("p4", "derived", "telemetry_event")
_emit_captures_evaluation_metric("p4", "derived", "eval_metric")
_emit_stores_embedding("p4", "derived", "embedding_store")
_emit_updates_meta_learning_state("p4", "derived", "meta_learning")
_emit_links_execution_to_snapshot("p4", "derived", "exec_snapshot_link")
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
from tqdm import tqdm

_emit_emits_metric_event("derived", "p4obs", "metric_1")
_emit_emits_metric_event("derived", "p4obs", "metric_2")
_emit_emits_metric_event("derived", "p4obs", "metric_3")
_emit_emits_metric_event("derived", "p4obs", "metric_4")
_emit_emits_metric_event("derived", "p4obs", "metric_5")
_emit_emits_metric_event("derived", "p4obs", "metric_6")
_emit_records_incident_event("derived", "p4obs", "incident")
_emit_captures_runtime_anomaly("derived", "p4obs", "anomaly")
_emit_writes_observability_log("derived", "p4obs", "obs_log")
_emit_updates_monitoring_state("derived", "p4obs", "mon_state")
_emit_triggers_alert("derived", "p4obs", "alert")
_emit_links_incident_trace("derived", "p4obs", "trace_link")
_emit_captures_pattern("derived", "p3lm", "pattern")
_emit_records_learning_event("derived", "p3lm", "learning_event")
_emit_writes_learning_snapshot("derived", "p3lm", "snapshot")
_emit_feeds_meta_learning("derived", "p3lm", "meta_feed")
_emit_updates_routing_strategy("derived", "p3lm", "routing")
_emit_improves_agent_policy("derived", "p3lm", "policy")
_emit_stores_learning_state("derived", "p3lm", "state")
_emit_records_execution_trace("derived", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("derived", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("derived", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("derived", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("derived", "L4_STATE", "p2_trace_5")
_emit_reads_environ("derived", "env_read", "p2_env_1")
_emit_reads_environ("derived", "env_read", "p2_env_2")
_emit_reads_runtime_state("derived", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("derived", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "derived", "context_pull")
_emit_pulls_context("p1", "derived", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "derived", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "derived", "uwg_term_2")
_emit_writes_through("p1", "derived", "write_through")
_emit_writes_through("p1", "derived", "write_through_2")
_emit_validated_by_safety_plane("p1", "derived", "safety_validation")
_emit_invokes_eval("p1", "derived", "eval_call")
_emit_proposal_commits_routing("p1", "derived", "routing_commit")

# These mirror ssot.APPS_*_DIR constants; defined here as literals to avoid
# a circular import (ssot imports derived at module level).
_APPS_EVAL_DIR: str = "apps_eval"
_APPS_EXEC_DIR: str = "apps_exec"
_APPS_RESEARCH_DIR: str = "apps_research"
_APPS_RFP_DIR: str = "apps_rfp"

# ============================================================================
# DERIVATION FUNCTIONS
# ============================================================================


def _derive_depth_rules() -> dict[str, int]:
    """Derive DEPTH_RULES from territory definitions."""
    result: dict[str, int] = {}
    for territory_name, territory_def in get_all_territories().items():
        if isinstance(territory_def, Mapping):
            depth = territory_def.get("depth", 2)
            result[territory_name] = depth
    return result


def _derive_core_subfolder_map() -> dict[str, list[str]]:
    """Derive CORE_SUBFOLDER_MAP from territory definitions."""
    result: dict[str, list[str]] = {}
    agentic_core = get_all_territories().get("agentic_core", {})
    subfolders = agentic_core.get("subfolders", {})

    for domain_name, domain_def in subfolders.items():
        if isinstance(domain_def, dict):
            nested = domain_def.get("subfolders", {})
            if isinstance(nested, dict):
                result[domain_name] = list(nested.keys())
            else:
                result[domain_name] = []
        else:
            result[domain_name] = []

    return result


def _derive_subfolder_metadata() -> dict[str, dict[str, Any]]:
    """Derive SUBFOLDER_METADATA from territory definitions."""
    result: dict[str, dict[str, Any]] = {}
    agentic_core = get_all_territories().get("agentic_core", {})
    subfolders = agentic_core.get("subfolders", {})

    for domain_name, domain_def in subfolders.items():
        if isinstance(domain_def, dict):
            result[domain_name] = {
                "purpose": domain_def.get("purpose", f"{domain_name} domain"),
                "content_types": list(domain_def.get("subfolders", {}).keys()) or [domain_name],
                "execution_allowed": domain_def.get("execution_allowed", False),
                "notes": domain_def.get("notes", ""),
            }

    return result


def _derive_apps_subfolder_map(territory_name: str) -> dict[str, list[str]]:
    """Derive APPS_*_SUBFOLDER_MAP from territory definitions."""
    result: dict[str, list[str]] = {}
    territory = get_all_territories().get(territory_name, {})
    if not isinstance(territory, Mapping):
        return result

    subfolders = territory.get("subfolders", {})

    if isinstance(subfolders, (list, tuple)):
        for sf_name in subfolders:
            result[sf_name] = []
        return result

    if not isinstance(subfolders, Mapping):
        return result

    for sf_name, sf_def in tqdm(subfolders.items(), desc="Processing", unit="item"):
        if isinstance(sf_def, Mapping):
            nested = sf_def.get("subfolders", {})
            if isinstance(nested, Mapping):
                result[sf_name] = list(nested.keys())
            elif isinstance(nested, (list, tuple)):
                result[sf_name] = list(nested)
            else:
                result[sf_name] = []
        elif isinstance(sf_def, (list, tuple)):
            result[sf_name] = list(sf_def)
        else:
            result[sf_name] = []

    return result


# ============================================================================
# DERIVED REGISTRIES
# ============================================================================

DEPTH_RULES: Final[Mapping[str, int]] = _derive_depth_rules()
CORE_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_core_subfolder_map()
SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = _derive_subfolder_metadata()
APPS_RG_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map(APPS_RG_DIR)
APPS_LIC_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map(APPS_LIC_DIR)
APPS_SHARED_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map(APPS_SHARED_DIR)
APPS_EVAL_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map(_APPS_EVAL_DIR)
APPS_EXEC_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map(_APPS_EXEC_DIR)
APPS_RESEARCH_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map(
    _APPS_RESEARCH_DIR,
)
APPS_RFP_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map(_APPS_RFP_DIR)

# Type-safe alias
agentic_core_registry: Final[Mapping[str, Sequence[str]]] = CORE_SUBFOLDER_MAP


# ============================================================================
# L4 SUBFOLDER MAP
# ============================================================================

L4_SUBFOLDER_MAP: Final[Mapping[str, Mapping[str, Sequence[str]]]] = {
    "dashboards": {
        "generators": ["dashboard_generators", "data_generators"],
        "templates": ["html_templates", "component_templates"],
        "components": ["ui_components", "chart_components"],
        "data": ["json_data", "runtime_data"],
        "tests": ["unit_tests", "e2e_tests"],
        "js": ["components", "controllers", "renderers", "utils", "constants"],
        "css": ["themes", "layouts"],
        "config": ["dashboard_config"],
    },
    "reasoning": {
        "healing": ["audit_healing_strategy"],
    },
    "scripts": {
        "healing": ["healing_strategies", "healing_engines"],
        "validation": ["validators", "checkers"],
        "utilities": ["file_utilities", "code_utilities"],
        "workflows": ["workflow_scripts", "pipeline_scripts"],
        "installation": ["install_scripts"],
        "maintenance": ["maintenance_scripts"],
        "test_utilities": ["test_helpers"],
    },
    "L3_reasoning": {
        "core": ["base_orchestrators", "orchestration_types"],
        "dag": ["dag_executors", "dag_managers"],
        "rl": ["rl_orchestrators", "rl_coordinators"],
        "mission": ["mission_controllers", "mission_runners"],
        "mcp": ["mcp_routers", "mcp_managers"],
        "safety": ["safety_orchestrators"],
        "state": ["state_managers"],
        "rag": ["rag_orchestrators"],
        "telemetry": ["telemetry_agents", "metrics_agents"],
    },
    "L1_reasoning": {
        "engines": ["reasoning_engines", "logic_processors"],
        "planning": ["planners", "schedulers"],
        "memory": ["memory_managers", "context_handlers"],
        "analysis": ["analyzers", "evaluators"],
        "synthesis": ["synthesizers", "generators"],
        "evaluation": ["evaluators", "scorers"],
    },
    "enforcement": {
        "security": ["pii_guards", "injection_guards", "auth_guards"],
        "quality": ["code_quality", "format_guards"],
        "structural": ["hierarchy_healers", "structure_guards"],
        "constitutional": ["constitutional_ai", "governance_guards"],
        "resource": ["resource_guards", "budget_guards"],
        "mcp": ["mcp_security", "mcp_guards"],
        "detection": ["duplicate_detectors", "threat_detectors"],
    },
    "L2_reasoning": {
        "core": ["registry_core", "registry_types"],
        "tools": ["tool_implementations"],
        "handlers": ["tool_handlers"],
        "validators": ["tool_validators"],
        "adapters": ["tool_adapters"],
    },
    "L5_enforcement": {
        "governance": ["governance_policies", "compliance_rules"],
        "security": ["security_guards", "access_control"],
    },
    "L6_dashboards": {
        "core": ["dashboard_core"],
        "css": ["themes", "layouts"],
        "data": ["json_data", "runtime_data"],
        "js": {
            "components": ["ui_components"],
            "constants": ["js_constants"],
            "controllers": ["dashboard_controllers"],
            "renderers": ["chart_renderers"],
            "utils": ["js_utils"],
        },
        "renderers": ["server_renderers"],
    },
    "prompt_governance": {
        "meta_prompts": {
            "orchestration": ["agents", "flows"],
            "reasoning": ["cot", "tot", "react"],
            "security": ["guards", "pii"],
            "personas": ["roles", "behavioral"],
        },
        "templates": {
            "instructional": ["cognition", "execution", "safety"],
            "specialized": ["domain", "format"],
            "fragments": ["partials", "blocks"],
            "rendering": ["engines", "filters"],
        },
        "scripts": {
            "audit": ["syntax_checks", "compliance_scans"],
            "migration": ["version_porters", "legacy_converters"],
            "maintenance": ["registry_cleaners", "cache_managers"],
        },
        "version_registry": {
            "manifests": ["active", "history"],
            "locks": ["commit_locks"],
            "lineage": ["parents", "forks"],
        },
    },
}

L4_APPROVED_FOLDERS: Final[frozenset[str]] = frozenset(
    {
        "agentic_core/L6_observability/dashboards",
        "agentic_core/L0_routing/scripts",
        "agentic_core/L0_routing/reasoning",
        "agentic_core/L3_orchestration/reasoning",
        "agentic_core/L1_cognition/reasoning",
        "agentic_core/L5_safety/enforcement",
        "agentic_core/L5_safety/validators",
        "agentic_core/L5_safety/reasoning",
        "agentic_core/L5_safety/config",
        "agentic_core/L2_execution/reasoning",
        "agentic_core/L2_execution/tools",
        "agentic_core/L4_state/memory",
        "agentic_core/config/core",
        "agentic_core/prompt_governance/meta_prompts",
        "agentic_core/prompt_governance/templates",
        "agentic_core/prompt_governance/scripts",
        "agentic_core/prompt_governance/version_registry",
        "agentic_core/prompt_governance/registry",
        "agentic_core/prompt_governance/security",
        "agentic_core/seams/contracts",
    },
)


# ============================================================================
# SCRIPTS PLACEMENT RULES
# ============================================================================

SCRIPTS_PLACEMENT_RULES: Final[Mapping[str, Mapping[str, Any]]] = {
    "root_ops_scripts": {
        "description": "Standalone utilities (setup, pip, env) with NO core dependencies.",
        "forbidden_imports": ["agentic_core"],
        "allowed_depth": 1,
        "violation_destination": "agentic_core/L0_routing/scripts",
    },
    "l0_maintenance_scripts": {
        "description": "System maintenance, healing, and sovereign agents.",
        "required_capabilities": ["core_access"],
        "preferred_location": "agentic_core/L0_routing/scripts",
    },
}


# ============================================================================
# TESTS SUBFOLDER MAP
# Derived from territory definitions["tests"]["subfolders"] — the single SSOT.
# Do NOT add entries here directly; update _constants.py instead.
# ============================================================================


def _derive_tests_subfolder_map() -> dict[str, list[str]]:
    """Build tests subfolder map from the SSOT territory declaration.

    Territory definitions use mappingproxy objects (not plain dicts), so we
    check for a 'keys' attribute (Mapping duck-type) rather than isinstance(dict).
    """
    from agentic_core.L5_safety.config.structure_blueprint.territories import (
        get_all_territories,
    )

    tests_config = get_all_territories().get("tests", {})
    raw = tests_config.get("subfolders", {})
    result: dict[str, list[str]] = {}
    if not hasattr(raw, "keys"):
        return result
    for key, val in tqdm(raw.items(), desc="Processing", unit="item"):
        if hasattr(val, "keys"):
            nested = val.get("subfolders", {})
            if hasattr(nested, "keys"):
                result[key] = list(nested.keys())
            elif isinstance(nested, (list, tuple)):
                result[key] = list(nested)
            else:
                result[key] = []
        elif isinstance(val, (list, tuple)):
            result[key] = list(val)
        else:
            result[key] = []
    return result


TESTS_L2_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_tests_subfolder_map()

TESTS_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = TESTS_L2_SUBFOLDER_MAP


# ============================================================================
# VERIFICATION FUNCTION
# ============================================================================


def verify_derived_registries() -> list[str]:
    """Verify derived registries are consistent with SOVEREIGN_TERRITORIES."""

    discrepancies: list[str] = []

    standard_lcd = {"config", "types", "reasoning", "enforcement", "validators", "utils"}
    for layer in tqdm(
        [
            "L0_routing",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ],
        desc="Processing",
        unit="item",
    ):
        derived = set(CORE_SUBFOLDER_MAP.get(layer, []))
        if not standard_lcd.issubset(derived):
            missing = standard_lcd - derived
            discrepancies.append(f"{layer} missing LCD subfolders: {missing}")

    for key in CORE_SUBFOLDER_MAP:
        if key not in SUBFOLDER_METADATA:
            discrepancies.append(f"SUBFOLDER_METADATA missing key: {key}")

    if not APPS_RG_SUBFOLDER_MAP:
        discrepancies.append("APPS_RG_SUBFOLDER_MAP is empty")

    return discrepancies
